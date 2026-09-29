import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.Vector;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;

import javax.microedition.media.Control;
import javax.microedition.media.Manager;
import javax.microedition.media.MediaException;
import javax.microedition.media.Player;
import javax.microedition.media.PlayerListener;
import javax.microedition.media.TimeBase;
import javax.microedition.media.control.StopTimeControl;
import javax.microedition.media.control.VolumeControl;
import javax.microedition.media.protocol.ContentDescriptor;
import javax.microedition.media.protocol.DataSource;
import javax.microedition.media.protocol.SourceStream;

import com.hd2.media.AudioDuration;

/**
 * Bounded host tests for the already-compiled 989 shared silent playback
 * classes.  This source deliberately contains no target-only APIs, no native
 * calls, and no writes to the source game JAR.
 */
public final class Silent989HostTests {
    private int assertions;
    private int failures;
    private int cases;
    private int passedCases;
    private final Vector failureText = new Vector();
    private final Vector climateResults = new Vector();
    private final String climateJar;

    private Silent989HostTests(String jarPath) {
        climateJar = jarPath;
    }

    private interface Checked {
        void run() throws Exception;
    }

    private void line(String s) {
        System.out.println(s);
    }

    private void check(boolean condition, String name) {
        ++assertions;
        if (!condition) {
            ++failures;
            String text = "FAIL " + name;
            failureText.addElement(text);
            line(text);
        }
    }

    private void checkEquals(long expected, long actual, String name) {
        check(expected == actual, name + " expected=" + expected + " actual=" + actual);
    }

    private void checkEquals(String expected, String actual, String name) {
        check(expected == null ? actual == null : expected.equals(actual),
                name + " expected=" + expected + " actual=" + actual);
    }

    private void expect(final Class wanted, Checked action, String name) {
        ++assertions;
        try {
            action.run();
            ++failures;
            String text = "FAIL " + name + " expected=" + wanted.getName() + " actual=none";
            failureText.addElement(text);
            line(text);
        } catch (Throwable t) {
            if (!wanted.isAssignableFrom(t.getClass())) {
                ++failures;
                String text = "FAIL " + name + " expected=" + wanted.getName()
                        + " actual=" + t.getClass().getName() + ":" + String.valueOf(t.getMessage());
                failureText.addElement(text);
                line(text);
            }
        }
    }

    private void runCase(String name, Checked action) {
        ++cases;
        line("CASE " + name + " START");
        int before = failures;
        try {
            action.run();
        } catch (Throwable t) {
            ++failures;
            String text = "FAIL " + name + " uncaught=" + t.getClass().getName()
                    + ":" + String.valueOf(t.getMessage());
            failureText.addElement(text);
            line(text);
            t.printStackTrace(System.out);
        }
        if (before == failures) {
            ++passedCases;
            line("CASE " + name + " PASS");
        } else {
            line("CASE " + name + " FAIL");
        }
    }

    private static class Probe implements PlayerListener {
        private final Vector names = new Vector();
        private final Vector values = new Vector();

        public synchronized void playerUpdate(Player player, String event, Object data) {
            names.addElement(event);
            values.addElement(data);
            notifyAll();
        }

        public synchronized int count(String event) {
            int n = 0;
            for (int i = 0; i < names.size(); ++i)
                if (event.equals(names.elementAt(i))) ++n;
            return n;
        }

        public synchronized int size() {
            return names.size();
        }

        public synchronized String at(int index) {
            return (String) names.elementAt(index);
        }

        public synchronized Object valueAt(int index) {
            return values.elementAt(index);
        }

        public synchronized boolean awaitCount(String event, int wanted, long timeoutMs) {
            long end = System.currentTimeMillis() + timeoutMs;
            while (count(event) < wanted) {
                long left = end - System.currentTimeMillis();
                if (left <= 0) return false;
                try { wait(left); } catch (InterruptedException e) { return false; }
            }
            return true;
        }

        public synchronized boolean awaitSize(int wanted, long timeoutMs) {
            long end = System.currentTimeMillis() + timeoutMs;
            while (names.size() < wanted) {
                long left = end - System.currentTimeMillis();
                if (left <= 0) return false;
                try { wait(left); } catch (InterruptedException e) { return false; }
            }
            return true;
        }

        public synchronized boolean sequence(String[] expected) {
            if (names.size() < expected.length) return false;
            for (int i = 0; i < expected.length; ++i)
                if (!expected[i].equals(names.elementAt(i))) return false;
            return true;
        }
    }

    private static final class ReentrantCloser extends Probe {
        private boolean closedFromCallback;

        public synchronized void playerUpdate(Player player, String event, Object data) {
            super.playerUpdate(player, event, data);
            if (PlayerListener.STARTED.equals(event) && !closedFromCallback) {
                closedFromCallback = true;
                player.close();
            }
        }
    }

    private static final class ThrowingListener implements PlayerListener {
        public void playerUpdate(Player player, String event, Object data) {
            throw new RuntimeException("intentional test listener failure");
        }
    }

    private static final class CountingInput extends ByteArrayInputStream {
        private boolean closed;

        CountingInput(byte[] data) { super(data); }

        public void close() throws IOException {
            closed = true;
            super.close();
        }
    }

    private static class MemSource extends DataSource {
        private final String type;
        private final byte[] data;
        int connects;
        int starts;
        int stops;
        int disconnects;

        MemSource(String type, byte[] data) {
            super("file:///host-test");
            this.type = type;
            this.data = data;
        }

        public String getContentType() { return type; }
        public void connect() { ++connects; }
        public void disconnect() { ++disconnects; }
        public void start() { ++starts; }
        public void stop() { ++stops; }
        public Control getControl(String name) { return null; }
        public Control[] getControls() { return new Control[0]; }
        public SourceStream[] getStreams() {
            return new SourceStream[] { new MemStream(data) };
        }
    }

    private static final class MemStream implements SourceStream {
        private final byte[] data;
        private int pos;

        MemStream(byte[] bytes) { data = bytes; }

        public ContentDescriptor getContentDescriptor() { return new ContentDescriptor("audio/x-wav"); }
        public long getContentLength() { return data.length; }
        public int read(byte[] b, int off, int len) {
            if (pos >= data.length) return -1;
            int n = Math.min(len, data.length - pos);
            System.arraycopy(data, pos, b, off, n);
            pos += n;
            return n;
        }
        public int getTransferSize() { return 1; }
        public long seek(long where) { if (where < 0 || where > data.length) return -1; pos = (int) where; return pos; }
        public long tell() { return pos; }
        public int getSeekType() { return SourceStream.NOT_SEEKABLE; }
        public Control getControl(String name) { return null; }
        public Control[] getControls() { return new Control[0]; }
    }

    private static final class BadDataSource extends MemSource {
        BadDataSource(byte[] data) { super("audio/ogg", data); }
    }

    private static byte[] ascii(String value) {
        byte[] result = new byte[value.length()];
        for (int i = 0; i < value.length(); ++i) result[i] = (byte) value.charAt(i);
        return result;
    }

    private static void putAscii(byte[] b, int at, String s) {
        byte[] x = ascii(s);
        System.arraycopy(x, 0, b, at, x.length);
    }

    private static void le16(byte[] b, int at, int value) {
        b[at] = (byte) value;
        b[at + 1] = (byte) (value >> 8);
    }

    private static void le32(byte[] b, int at, long value) {
        le16(b, at, (int) value);
        le16(b, at + 2, (int) (value >> 16));
    }

    private static void be16(ByteArrayOutputStream out, int value) {
        out.write((value >> 8) & 255);
        out.write(value & 255);
    }

    private static void be32(ByteArrayOutputStream out, long value) {
        out.write((int) (value >> 24) & 255);
        out.write((int) (value >> 16) & 255);
        out.write((int) (value >> 8) & 255);
        out.write((int) value & 255);
    }

    private static byte[] wav(int sampleRate, int channels, int bits, int frames) {
        int align = channels * (bits / 8);
        int dataBytes = align * frames;
        byte[] b = new byte[44 + dataBytes];
        putAscii(b, 0, "RIFF");
        le32(b, 4, 36 + dataBytes);
        putAscii(b, 8, "WAVE");
        putAscii(b, 12, "fmt ");
        le32(b, 16, 16);
        le16(b, 20, 1);
        le16(b, 22, channels);
        le32(b, 24, sampleRate);
        le32(b, 28, sampleRate * align);
        le16(b, 32, align);
        le16(b, 34, bits);
        putAscii(b, 36, "data");
        le32(b, 40, dataBytes);
        return b;
    }

    private static byte[] mp3Frame() {
        /* MPEG-2 Layer III, 64 kbps, 22050 Hz: the parser's frame size is 208. */
        byte[] b = new byte[208];
        b[0] = (byte) 0xff;
        b[1] = (byte) 0xf3;
        b[2] = (byte) 0x80;
        b[3] = (byte) 0xc4;
        return b;
    }

    private static byte[] midi() {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        out.write('M'); out.write('T'); out.write('h'); out.write('d');
        be32(out, 6); be16(out, 0); be16(out, 1); be16(out, 480);
        ByteArrayOutputStream track = new ByteArrayOutputStream();
        track.write(0); track.write(0xff); track.write(0x51); track.write(3);
        track.write(0x07); track.write(0xa1); track.write(0x20);
        track.write(0x83); track.write(0x60); track.write(0x90); track.write(60); track.write(64);
        track.write(0x83); track.write(0x60); track.write(0x80); track.write(60); track.write(0);
        track.write(0); track.write(0xff); track.write(0x2f); track.write(0);
        byte[] t = track.toByteArray();
        out.write('M'); out.write('T'); out.write('r'); out.write('k'); be32(out, t.length);
        out.write(t, 0, t.length);
        return out.toByteArray();
    }

    private static byte[] truncate(byte[] input, int length) {
        byte[] b = new byte[length];
        System.arraycopy(input, 0, b, 0, length);
        return b;
    }

    private static Player make(byte[] bytes, String type) throws Exception {
        return Manager.createPlayer(new ByteArrayInputStream(bytes), type);
    }

    private static void closeQuietly(Player player) {
        if (player != null) {
            try { player.close(); } catch (Throwable ignored) { }
        }
    }

    private void testSurface() throws Exception {
        String[] all = Manager.getSupportedContentTypes(null);
        check(all.length == 3, "surface.types.count");
        checkEquals("audio/mpeg", all[0], "surface.types.mp3");
        checkEquals("audio/midi", all[1], "surface.types.midi");
        checkEquals("audio/x-wav", all[2], "surface.types.wav");
        check(Manager.getSupportedContentTypes("file").length == 3, "surface.types.file");
        check(Manager.getSupportedContentTypes("http").length == 0, "surface.types.http.rejected");
        check(Manager.getSupportedProtocols("audio/mpeg").length == 1, "surface.protocol.mp3");
        checkEquals("file", Manager.getSupportedProtocols("audio/mp3")[0], "surface.protocol.alias");
        check(Manager.getSupportedProtocols("video/mp4").length == 0, "surface.protocol.video.rejected");
        TimeBase clock = Manager.getSystemTimeBase();
        check(clock != null, "surface.timebase.nonnull");
        long c1 = clock.getTime();
        long c2 = clock.getTime();
        check(c2 >= c1, "surface.timebase.monotonic.host");

        final Player p = make(wav(8000, 1, 8, 800), "audio/x-wav");
        checkEquals(Player.UNREALIZED, p.getState(), "surface.initial.state");
        checkEquals(100000L, p.getDuration(), "surface.duration");
        expect(IllegalStateException.class, new Checked() {
            public void run() { p.getContentType(); }
        }, "surface.content.before.realize");
        expect(IllegalStateException.class, new Checked() {
            public void run() { p.getControl("VolumeControl"); }
        }, "surface.control.before.realize");
        p.realize();
        checkEquals(Player.REALIZED, p.getState(), "surface.realized.state");
        checkEquals("audio/x-wav", p.getContentType(), "surface.content.after.realize");
        p.prefetch();
        checkEquals(Player.PREFETCHED, p.getState(), "surface.prefetched.state");
        Control[] controls = p.getControls();
        check(controls.length == 2, "surface.controls.count");
        check(p.getControl("VolumeControl") != null, "surface.volume.control");
        check(p.getControl("javax.microedition.media.control.StopTimeControl") != null,
                "surface.stoptime.control");
        check(p.getControl("javax.microedition.media.control.MIDIControl") == null,
                "surface.unsupported.control.null");
        p.close();
        checkEquals(Player.CLOSED, p.getState(), "surface.closed.state");
        p.close();
        expect(IllegalStateException.class, new Checked() {
            public void run() { p.getDuration(); }
        }, "surface.closed.duration");
    }

    private void testLifecycleSeekRestart() throws Exception {
        final Player p = make(wav(8000, 1, 8, 1000), "audio/x-wav");
        final Probe probe = new Probe();
        p.realize();
        p.prefetch();
        p.addPlayerListener(probe);
        checkEquals(0L, p.setMediaTime(-10), "lifecycle.seek.clamp.low");
        checkEquals(125000L, p.setMediaTime(999999), "lifecycle.seek.clamp.high");
        checkEquals(62500L, p.setMediaTime(62500), "lifecycle.seek.middle");
        p.start();
        checkEquals(Player.STARTED, p.getState(), "lifecycle.start.state");
        check(probe.awaitCount(PlayerListener.STARTED, 1, 500), "lifecycle.started.event");
        p.stop();
        checkEquals(Player.PREFETCHED, p.getState(), "lifecycle.stop.state");
        check(probe.awaitCount(PlayerListener.STOPPED, 1, 500), "lifecycle.stopped.event");
        check(p.getMediaTime() >= 62500L && p.getMediaTime() <= 125000L,
                "lifecycle.stop.position.in.range");
        p.start();
        check(probe.awaitCount(PlayerListener.STARTED, 2, 500), "lifecycle.restart.started");
        p.stop();
        p.deallocate();
        checkEquals(Player.REALIZED, p.getState(), "lifecycle.deallocate.state");
        p.prefetch();
        p.start();
        check(probe.awaitCount(PlayerListener.STARTED, 3, 500), "lifecycle.start.after.deallocate");
        p.stop();
        p.close();
    }

    private void testLoops() throws Exception {
        final Player p = make(wav(8000, 1, 8, 240), "audio/x-wav");
        final Probe probe = new Probe();
        p.realize();
        p.setLoopCount(2);
        p.addPlayerListener(probe);
        p.start();
        check(probe.awaitSize(4, 1200), "loops.finite.events.arrive");
        check(probe.sequence(new String[] { PlayerListener.STARTED, PlayerListener.END_OF_MEDIA,
                PlayerListener.STARTED, PlayerListener.END_OF_MEDIA }), "loops.end-start.order");
        checkEquals(Player.PREFETCHED, p.getState(), "loops.final.state");
        checkEquals(2L, probe.count(PlayerListener.END_OF_MEDIA), "loops.end.count");
        checkEquals(2L, probe.count(PlayerListener.STARTED), "loops.started.count");
        checkEquals(30000L, ((Long) probe.valueAt(1)).longValue(), "loops.first.end.position");
        p.start();
        check(probe.awaitCount(PlayerListener.STARTED, 3, 500), "loops.restart.started");
        p.stop();
        p.close();

        final Player infinite = make(wav(8000, 1, 8, 160), "audio/x-wav");
        final Probe ip = new Probe();
        infinite.realize();
        infinite.setLoopCount(-1);
        infinite.addPlayerListener(ip);
        infinite.start();
        check(ip.awaitCount(PlayerListener.END_OF_MEDIA, 2, 1000), "loops.infinite.progress");
        check(ip.count(PlayerListener.STARTED) >= 3, "loops.infinite.restart.events");
        infinite.stop();
        infinite.close();

        final Player zero = make(wav(8000, 1, 8, 0), "audio/x-wav");
        zero.realize();
        zero.setLoopCount(-1);
        expect(MediaException.class, new Checked() {
            public void run() throws Exception { zero.start(); }
        }, "loops.zero.infinite.rejected");
        zero.close();

        final Player invalid = make(wav(8000, 1, 8, 800), "audio/x-wav");
        invalid.realize();
        expect(IllegalArgumentException.class, new Checked() {
            public void run() { invalid.setLoopCount(0); }
        }, "loops.zero.count.rejected");
        expect(IllegalArgumentException.class, new Checked() {
            public void run() { invalid.setLoopCount(-2); }
        }, "loops.negative.count.rejected");
        invalid.start();
        expect(IllegalStateException.class, new Checked() {
            public void run() { invalid.setLoopCount(2); }
        }, "loops.change.while.started.rejected");
        invalid.close();
    }

    private void testVolumeAndStopTime() throws Exception {
        final Player p = make(wav(8000, 1, 8, 2000), "audio/x-wav");
        final Probe probe = new Probe();
        p.realize();
        VolumeControl volume = (VolumeControl) p.getControl("VolumeControl");
        StopTimeControl stopTime = (StopTimeControl) p.getControl("StopTimeControl");
        p.addPlayerListener(probe);
        checkEquals(100L, volume.getLevel(), "volume.initial.level");
        check(!volume.isMuted(), "volume.initial.unmuted");
        checkEquals(35L, volume.setLevel(35), "volume.set.level");
        volume.setMute(true);
        check(volume.isMuted(), "volume.mute.true");
        volume.setMute(false);
        check(!volume.isMuted(), "volume.mute.false");
        /* The callback worker is asynchronous; retain the count in the log if it regresses. */
        boolean volumeEvents = probe.awaitCount(PlayerListener.VOLUME_CHANGED, 3, 500);
        line("VOLUME_EVENTS_AFTER " + probe.count(PlayerListener.VOLUME_CHANGED));
        check(volumeEvents, "volume.events");

        checkEquals(StopTimeControl.RESET, stopTime.getStopTime(), "stoptime.initial.reset");
        boolean stopTimeSet = true;
        try {
            stopTime.setStopTime(50000L);
        } catch (Throwable t) {
            stopTimeSet = false;
            check(false, "stoptime.set.no.exception " + t.getClass().getName());
        }
        checkEquals(50000L, stopTime.getStopTime(), "stoptime.set");
        p.start();
        check(probe.awaitCount(PlayerListener.STOPPED_AT_TIME, 1, 800), "stoptime.event");
        checkEquals(Player.PREFETCHED, p.getState(), "stoptime.state");
        checkEquals(50000L, p.getMediaTime(), "stoptime.position");
        checkEquals(StopTimeControl.RESET, stopTime.getStopTime(), "stoptime.auto.reset");
        p.close();

        final Player running = make(wav(8000, 1, 8, 1000), "audio/x-wav");
        running.realize();
        running.start();
        StopTimeControl runningStop = (StopTimeControl) running.getControl("StopTimeControl");
        boolean runningStopSet = true;
        try {
            runningStop.setStopTime(30000L);
        } catch (Throwable t) {
            runningStopSet = false;
            check(false, "stoptime.running.first.set.no.exception " + t.getClass().getName());
        }
        if (runningStopSet) {
            expect(IllegalStateException.class, new Checked() {
                public void run() { runningStopSetAgain(running); }
            }, "stoptime.second.running.set.rejected");
        }
        running.close();

        final Player invalid = make(wav(8000, 1, 8, 100), "audio/x-wav");
        invalid.realize();
        final StopTimeControl invalidStop = (StopTimeControl) invalid.getControl("StopTimeControl");
        expect(IllegalArgumentException.class, new Checked() {
            public void run() { invalidStop.setStopTime(-2L); }
        }, "stoptime.negative.rejected");
        invalid.close();
    }

    private static void runningStopSetAgain(Player p) {
        ((StopTimeControl) p.getControl("StopTimeControl")).setStopTime(40000L);
    }

    private void testListenerReentrancyAndIsolation() throws Exception {
        final Player reentrant = make(wav(8000, 1, 8, 1600), "audio/x-wav");
        final ReentrantCloser closer = new ReentrantCloser();
        reentrant.realize();
        reentrant.addPlayerListener(closer);
        reentrant.start();
        check(closer.awaitCount(PlayerListener.CLOSED, 1, 700), "listener.reentrant.close.event");
        checkEquals(Player.CLOSED, reentrant.getState(), "listener.reentrant.closed.state");
        check(closer.closedFromCallback, "listener.reentrant.callback.did.close");
        check(closer.size() >= 2, "listener.reentrant.no.deadlock");

        final Player isolated = make(wav(8000, 1, 8, 800), "audio/x-wav");
        final Probe good = new Probe();
        isolated.realize();
        isolated.addPlayerListener(new ThrowingListener());
        isolated.addPlayerListener(good);
        isolated.start();
        check(good.awaitCount(PlayerListener.STARTED, 1, 500), "listener.thrower.isolated.started");
        check(good.awaitCount(PlayerListener.END_OF_MEDIA, 1, 800), "listener.thrower.isolated.end");
        isolated.close();
    }

    private void testConcurrentStopClose() throws Exception {
        final Player p = make(wav(8000, 1, 8, 4000), "audio/x-wav");
        final Vector errors = new Vector();
        p.realize();
        p.start();
        Thread stopper = new Thread(new Runnable() {
            public void run() {
                for (int i = 0; i < 100; ++i) {
                    try { p.stop(); }
                    catch (IllegalStateException expectedAfterClose) { }
                    catch (Throwable t) { synchronized (errors) { errors.addElement(t); } }
                }
            }
        }, "silent989-stop-race");
        Thread closer = new Thread(new Runnable() {
            public void run() {
                try {
                    Thread.sleep(5);
                    p.close();
                } catch (Throwable t) {
                    synchronized (errors) { errors.addElement(t); }
                }
            }
        }, "silent989-close-race");
        stopper.start();
        closer.start();
        stopper.join(1200);
        closer.join(1200);
        check(!stopper.isAlive(), "race.stopper.finished");
        check(!closer.isAlive(), "race.closer.finished");
        check(errors.size() == 0, "race.no.unexpected.errors");
        checkEquals(Player.CLOSED, p.getState(), "race.closed.state");
    }

    private void testParserAndDataSource() throws Exception {
        final byte[] validMp3 = mp3Frame();
        final byte[] validWav = wav(8000, 1, 8, 800);
        final byte[] validMidi = midi();
        final byte[] unknown = new byte[] { 1, 2, 3, 4, 5 };
        expect(MediaException.class, new Checked() {
            public void run() throws Exception { Manager.createPlayer(new ByteArrayInputStream(unknown), null); }
        }, "parser.unknown.detect");
        expect(MediaException.class, new Checked() {
            public void run() throws Exception { Manager.createPlayer(new ByteArrayInputStream(truncate(validMp3, 207)), "audio/mpeg"); }
        }, "parser.mp3.truncated");
        byte[] badWav = truncate(validWav, validWav.length - 1);
        final byte[] badWavFinal = badWav;
        expect(MediaException.class, new Checked() {
            public void run() throws Exception { Manager.createPlayer(new ByteArrayInputStream(badWavFinal), "audio/x-wav"); }
        }, "parser.wav.truncated");
        final byte[] badMidi = truncate(validMidi, validMidi.length - 1);
        expect(MediaException.class, new Checked() {
            public void run() throws Exception { Manager.createPlayer(new ByteArrayInputStream(badMidi), "audio/midi"); }
        }, "parser.midi.truncated");
        expect(MediaException.class, new Checked() {
            public void run() throws Exception { Manager.createPlayer(new ByteArrayInputStream(validWav), "audio/ogg"); }
        }, "parser.unsupported.type");
        expect(MediaException.class, new Checked() {
            public void run() throws Exception { Manager.createPlayer(new ByteArrayInputStream(unknown), "audio/mpeg"); }
        }, "parser.explicit.bad.payload");

        final CountingInput input = new CountingInput(validWav);
        Player owned = Manager.createPlayer(input, "audio/x-wav");
        check(!input.closed, "parser.caller.owns.input.close");
        owned.close();

        MemSource source = new MemSource("audio/x-wav", validWav);
        Player fromSource = Manager.createPlayer(source);
        checkEquals(100000L, fromSource.getDuration(), "datasource.duration");
        checkEquals(1L, source.connects, "datasource.connect");
        checkEquals(1L, source.starts, "datasource.start");
        checkEquals(1L, source.stops, "datasource.stop");
        checkEquals(1L, source.disconnects, "datasource.disconnect");
        fromSource.close();

        final BadDataSource badSource = new BadDataSource(validWav);
        expect(MediaException.class, new Checked() {
            public void run() throws Exception { Manager.createPlayer(badSource); }
        }, "datasource.unsupported.type");
        checkEquals(1L, badSource.connects, "datasource.bad.connect");
        checkEquals(0L, badSource.starts, "datasource.bad.not.started");
        checkEquals(0L, badSource.stops, "datasource.bad.not.stopped");
        checkEquals(1L, badSource.disconnects, "datasource.bad.disconnect");

        checkEquals(100000L, AudioDuration.measure(validWav, "audio/x-wav"), "parser.wav.duration");
        checkEquals(1000000L, AudioDuration.measure(validMidi, "audio/midi"), "parser.midi.duration");
        checkEquals(26122L, AudioDuration.measure(validMp3, "audio/mpeg"), "parser.mp3.duration");
    }

    private byte[] readEntry(JarFile jar, String name) throws Exception {
        JarEntry entry = jar.getJarEntry(name);
        check(entry != null, "climate." + name + ".present");
        InputStream in = jar.getInputStream(entry);
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] block = new byte[8192];
        for (;;) {
            int n = in.read(block);
            if (n < 0) break;
            if (n > 0) out.write(block, 0, n);
        }
        in.close();
        return out.toByteArray();
    }

    private void testClimateAssets() throws Exception {
        File file = new File(climateJar);
        check(file.isFile(), "climate.jar.exists");
        JarFile jar = new JarFile(file);
        String[] names = new String[] { "s1a", "s2a", "s3a", "s4a", "s5a", "s6a" };
        int[] expectedBytes = new int[] { 257043, 192679, 256626, 384731, 186618, 303856 };
        long[] expectedDurations = new long[] { 32130611L, 24084897L, 32078366L,
                48091426L, 23327346L, 37982039L };
        for (int i = 0; i < names.length; ++i) {
            String name = names[i];
            byte[] data = readEntry(jar, name);
            String detected = AudioDuration.detect(data);
            long duration = AudioDuration.measure(data, "audio/mpeg");
            Player p = Manager.createPlayer(new ByteArrayInputStream(data), null);
            p.realize();
            checkEquals("audio/mpeg", detected, "climate." + name + ".detect");
            checkEquals("audio/mpeg", p.getContentType(), "climate." + name + ".type");
            checkEquals(duration, p.getDuration(), "climate." + name + ".player.duration");
            checkEquals(expectedBytes[i], data.length, "climate." + name + ".bytes");
            checkEquals(expectedDurations[i], duration, "climate." + name + ".duration");
            check(duration > 0, "climate." + name + ".positive.duration");
            String result = name + " bytes=" + data.length + " duration_us=" + duration;
            climateResults.addElement(result);
            line("CLIMATE " + result);
            p.close();
        }
        jar.close();
    }

    private void runAll() {
        runCase("surface", new Checked() { public void run() throws Exception { testSurface(); } });
        runCase("lifecycle-seek-restart", new Checked() { public void run() throws Exception { testLifecycleSeekRestart(); } });
        runCase("loops", new Checked() { public void run() throws Exception { testLoops(); } });
        runCase("volume-stop-time", new Checked() { public void run() throws Exception { testVolumeAndStopTime(); } });
        runCase("listener-reentrancy-isolation", new Checked() { public void run() throws Exception { testListenerReentrancyAndIsolation(); } });
        runCase("concurrent-stop-close", new Checked() { public void run() throws Exception { testConcurrentStopClose(); } });
        runCase("parser-datasource", new Checked() { public void run() throws Exception { testParserAndDataSource(); } });
        runCase("climate-authentic-mp3", new Checked() { public void run() throws Exception { testClimateAssets(); } });
    }

    private void report() {
        line("TESTS_SUMMARY cases=" + cases + " passed_cases=" + passedCases
                + " failed_cases=" + (cases - passedCases) + " assertions=" + assertions
                + " failures=" + failures);
        for (int i = 0; i < climateResults.size(); ++i)
            line("TESTS_CLIMATE " + climateResults.elementAt(i));
        line("TESTS_TARGET_HARDWARE=NOT_TESTED");
        line("TESTS_SD_DEPLOYMENT=NOT_TOUCHED");
    }

    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("usage: Silent989HostTests <original-climate-jar>");
            System.exit(2);
        }
        Silent989HostTests tests = new Silent989HostTests(args[0]);
        tests.line("TESTS_START java=" + System.getProperty("java.version"));
        tests.line("TESTS_CLIMATE_JAR=" + args[0]);
        tests.runAll();
        tests.report();
        System.exit(tests.failures == 0 ? 0 : 1);
    }
}
