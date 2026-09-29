package com.hd2.media;

import java.util.Vector;
import javax.microedition.media.*;
import javax.microedition.media.control.VolumeControl;
import javax.microedition.media.control.StopTimeControl;

/** A real software timeline and state machine, with no native audio handles.
 * One short-lived worker per active Player; ordered callbacks run outside locks.
 * No worker is started by construction/realize and none remains idle after stop.
 */
public final class SilentPlayer implements Player, Runnable {
    private final String type;
    private final long duration;
    private final Vector listeners = new Vector();
    private final Vector events = new Vector();
    private final Volume volume = new Volume();
    private final StopTime stopTime = new StopTime();
    private int state = UNREALIZED, loops = 1, remaining = 1;
    private long position, lastClock, stopAt = StopTimeControl.RESET;
    private boolean finished, worker;
    private int level = 100;
    private boolean muted;

    SilentPlayer(String contentType, long length) {
        if (contentType == null || length < 0) throw new IllegalArgumentException("finite media required");
        type = contentType; duration = length;
    }
    private void open() { if (state == CLOSED) throw new IllegalStateException("Player CLOSED"); }
    private void realized() { open(); if (state == UNREALIZED) throw new IllegalStateException("Player UNREALIZED"); }
    private void kick() {
        if (!worker) {
            worker = true;
            try { new Thread(this).start(); }
            catch (RuntimeException e) { worker = false; throw e; }
            catch (Error e) { worker = false; throw e; }
        }
        notifyAll();
    }
    private void event(String name, Object data) {
        if (listeners.size() == 0) return;
        Object[] snapshot = new Object[listeners.size()]; listeners.copyInto(snapshot);
        events.addElement(new Object[] {name, data, snapshot});
        kick();
    }
    private void update() {
        if (state != STARTED) return;
        long now = SilentAudio.timeBase().getTime();
        long elapsed = now >= lastClock ? now - lastClock : 0;
        lastClock = now;
        // Saturation is explicit; never wrap media time if the wall clock jumps.
        position = elapsed > Long.MAX_VALUE - position ? Long.MAX_VALUE : position + elapsed;
        if (stopAt <= duration && position >= stopAt) {
            position = stopAt; stopAt = StopTimeControl.RESET; state = PREFETCHED;
            event(PlayerListener.STOPPED_AT_TIME, new Long(position)); return;
        }
        if (position >= duration) {
            position = duration; state = PREFETCHED;
            event(PlayerListener.END_OF_MEDIA, new Long(position));
            if (remaining == -1 || remaining > 1) {
                if (remaining > 1) --remaining;
                position = 0; state = STARTED;
                event(PlayerListener.STARTED, new Long(0));
                // A zero-length infinite loop cannot make timed progress.
                // Reject it in start(), rather than generating an event storm.
            } else { remaining = 0; finished = true; }
        }
    }
    public synchronized void realize() { open(); if (state == UNREALIZED) state = REALIZED; }
    public synchronized void prefetch() { realize(); if (state == REALIZED) state = PREFETCHED; }
    public synchronized void start() throws MediaException {
        open(); if (state == STARTED) return;
        prefetch();
        if (duration == 0 && loops == -1) throw new MediaException("Cannot infinitely loop zero-length media");
        if (finished || position >= duration) { position = 0; remaining = loops; finished = false; }
        // Reserve the worker before changing state, so failure cannot claim STARTED.
        kick(); lastClock = SilentAudio.timeBase().getTime(); state = STARTED;
        event(PlayerListener.STARTED, new Long(position));
    }
    public synchronized void stop() {
        open(); update();
        if (state == STARTED) { state = PREFETCHED; event(PlayerListener.STOPPED, new Long(position)); }
        notifyAll();
    }
    public synchronized void deallocate() {
        open(); stop(); if (state == PREFETCHED) state = REALIZED;
    }
    public synchronized void close() {
        if (state == CLOSED) return;
        // close cancels the timeline; only CLOSED is required, no fabricated device event.
        state = CLOSED;
        event(PlayerListener.CLOSED, null); listeners.removeAllElements(); notifyAll();
    }
    public synchronized int getState() { update(); return state; }
    public synchronized long getDuration() { open(); return duration; }
    public synchronized long getMediaTime() { open(); update(); return position; }
    public synchronized String getContentType() { realized(); return type; }
    public synchronized long setMediaTime(long time) {
        realized(); update();
        position = time < 0 ? 0 : (time > duration ? duration : time);
        lastClock = SilentAudio.timeBase().getTime(); finished = false;
        if (remaining == 0) remaining = loops;
        notifyAll(); return position;
    }
    public synchronized void setLoopCount(int count) {
        open(); update();
        if (state == STARTED) throw new IllegalStateException("Player STARTED");
        if (count == 0 || count < -1) throw new IllegalArgumentException("loop count");
        loops = remaining = count; finished = false;
    }
    public synchronized TimeBase getTimeBase() { realized(); return SilentAudio.timeBase(); }
    public synchronized void setTimeBase(TimeBase clock) throws MediaException {
        realized(); update();
        if (state == STARTED) throw new IllegalStateException("Player STARTED");
        if (clock != null && clock != SilentAudio.timeBase()) throw new MediaException("Only shared software TimeBase supported");
    }
    public synchronized void addPlayerListener(PlayerListener listener) {
        open(); if (listener != null && !listeners.contains(listener)) listeners.addElement(listener);
    }
    public synchronized void removePlayerListener(PlayerListener listener) {
        open(); listeners.removeElement(listener);
    }
    public synchronized Control getControl(String name) {
        realized(); if (name == null) throw new IllegalArgumentException("null control name");
        if (name.equals("VolumeControl") || name.equals("javax.microedition.media.control.VolumeControl")) return volume;
        if (name.equals("StopTimeControl") || name.equals("javax.microedition.media.control.StopTimeControl")) return stopTime;
        return null; // No false MIDI, video, recording or codec controls.
    }
    public synchronized Control[] getControls() { realized(); return new Control[] {volume, stopTime}; }
    public void run() {
        for (;;) {
            Object[] next;
            synchronized (this) {
                update();
                if (events.size() != 0) { next = (Object[])events.elementAt(0); events.removeElementAt(0); }
                else if (state != STARTED) { worker = false; return; }
                else {
                    long boundary = Math.min(duration, stopAt) - position;
                    long millis = Math.max(1L, Math.min(100L, (boundary + 999L) / 1000L));
                    try { wait(millis); } catch (InterruptedException e) { /* recheck state */ }
                    continue;
                }
            }
            Object[] targets = (Object[])next[2];
            for (int i = 0; i < targets.length; ++i) {
                try { ((PlayerListener)targets[i]).playerUpdate(this, (String)next[0], next[1]); }
                catch (RuntimeException e) {
                    // A broken listener must not strand the clock or the other listeners.
                    System.out.println("J9SIL989 listener RuntimeException");
                }
            }
        }
    }
    private final class Volume implements VolumeControl {
        public int getLevel() { synchronized (SilentPlayer.this) { open(); return level; } }
        public boolean isMuted() { synchronized (SilentPlayer.this) { open(); return muted; } }
        public int setLevel(int value) {
            synchronized (SilentPlayer.this) {
                open(); int n = Math.max(0, Math.min(100, value));
                if (level != n) { level = n; event(PlayerListener.VOLUME_CHANGED, this); }
                return level;
            }
        }
        public void setMute(boolean value) {
            synchronized (SilentPlayer.this) {
                open(); if (muted != value) { muted = value; event(PlayerListener.VOLUME_CHANGED, this); }
            }
        }
    }
    private final class StopTime implements StopTimeControl {
        public long getStopTime() { synchronized (SilentPlayer.this) { open(); return stopAt; } }
        public void setStopTime(long time) {
            synchronized (SilentPlayer.this) {
                open(); update();
                if (time < 0) throw new IllegalArgumentException("negative stop time");
                if (state == STARTED && stopAt != RESET) throw new IllegalStateException("Stop time already set");
                stopAt = time; update(); SilentPlayer.this.notifyAll();
            }
        }
    }
}
