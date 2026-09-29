package com.hd2.media;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import javax.microedition.io.Connector;
import javax.microedition.media.*;
import javax.microedition.media.protocol.*;

/** Finite-stream, software-timed SILENT backend. Never connects to audio HW. */
public final class SilentAudio {
    private static final int LIMIT = 8 * 1024 * 1024;
    private static int diagnostics;
    private static final TimeBase CLOCK = new TimeBase() {
        public long getTime() { return System.currentTimeMillis() * 1000L; }
    };
    private SilentAudio() {}
    public static TimeBase timeBase() { return CLOCK; }
    public static String canonical(String type) {
        if (type == null) return null;
        int semi = type.indexOf(';');
        String t = (semi < 0 ? type : type.substring(0, semi)).trim().toLowerCase();
        if (t.equals("audio/mpeg") || t.equals("audio/mp3") || t.equals("audio/x-mp3")) return "audio/mpeg";
        if (t.equals("audio/midi") || t.equals("audio/x-midi") || t.equals("audio/mid")) return "audio/midi";
        if (t.equals("audio/x-wav") || t.equals("audio/wav") || t.equals("audio/wave")) return "audio/x-wav";
        return null;
    }
    public static String[] types(String protocol) {
        if (protocol != null && !protocol.equals("file")) return new String[0];
        return new String[] {"audio/mpeg", "audio/midi", "audio/x-wav"};
    }
    public static String[] protocols(String type) {
        return type == null || canonical(type) != null ? new String[] {"file"} : new String[0];
    }
    private static synchronized void report(String type, long micros, int bytes) {
        if (diagnostics++ < 8)
            System.out.println(new StringBuffer("J9SIL989 backend=silent type=").append(type)
                .append(" duration_us=").append(micros).append(" bytes=").append(bytes).toString());
    }
    private static byte[] read(InputStream in) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] block = new byte[4096];
        int total = 0;
        for (;;) {
            int n = in.read(block);
            if (n < 0) break;
            if (n == 0) { int b = in.read(); if (b < 0) break; block[0] = (byte)b; n = 1; }
            if (n > LIMIT - total) throw new IOException("Silent playback: finite stream exceeds 8 MiB");
            out.write(block, 0, n); total += n;
        }
        return out.toByteArray();
    }
    public static Player create(InputStream in, String type) throws IOException, MediaException {
        if (in == null) throw new IllegalArgumentException("null stream");
        String t = canonical(type);
        if (type != null && t == null) throw new MediaException("Silent playback: unsupported media type");
        // Caller owns the InputStream. Consume it, but do not close it behind the caller.
        byte[] content = read(in);
        if (t == null) t = AudioDuration.detect(content);
        long duration = AudioDuration.measure(content, t);
        report(t, duration, content.length);
        return new SilentPlayer(t, duration);
    }
    public static Player create(String locator) throws IOException, MediaException {
        if (locator == null) throw new IllegalArgumentException("null locator");
        // No synthetic capture, network access, video or interactive MIDI device.
        if (!locator.startsWith("file:///"))
            throw new MediaException("Silent playback: only finite file locators supported; no capture/device input");
        InputStream in = Connector.openInputStream(locator);
        try { return create(in, null); } finally { in.close(); }
    }
    public static Player create(final DataSource source) throws IOException, MediaException {
        if (source == null) throw new IllegalArgumentException("null source");
        String locator = source.getLocator();
        if (locator != null && (locator.startsWith("capture:") || locator.startsWith("device:")))
            throw new MediaException("Silent playback does not provide capture or device input");
        boolean connected = false, started = false;
        try {
            source.connect(); connected = true;
            String type = source.getContentType();
            if (canonical(type) == null) throw new MediaException("Silent playback: unsupported DataSource type");
            SourceStream[] streams = source.getStreams();
            if (streams == null || streams.length != 1 || streams[0] == null ||
                streams[0].getContentLength() < 0 || streams[0].getContentLength() > LIMIT)
                throw new MediaException("Silent playback: one finite stream required");
            final SourceStream stream = streams[0];
            source.start(); started = true;
            return create(new InputStream() {
                public int read() throws IOException {
                    byte[] one = new byte[1]; int n = stream.read(one, 0, 1);
                    if (n == 0) throw new IOException("Non-progressing source");
                    return n < 0 ? -1 : one[0] & 255;
                }
                public int read(byte[] b, int off, int n) throws IOException { return stream.read(b, off, n); }
            }, type);
        } finally {
            try { if (started) source.stop(); } finally { if (connected) source.disconnect(); }
        }
    }
    public static void playTone(int note, int millis, int volume) throws MediaException {
        if (note < 0 || note > 127 || millis <= 0) throw new IllegalArgumentException("tone note/duration");
        SilentPlayer p = new SilentPlayer("audio/x-tone-seq", millis * 1000L);
        p.realize();
        ((javax.microedition.media.control.VolumeControl)p.getControl("VolumeControl")).setLevel(volume);
        report("audio/x-tone-seq", millis * 1000L, 0);
        p.start();
    }
}
