package javax.microedition.media;

import java.io.IOException;
import java.io.InputStream;
import com.hd2.media.SilentAudio;
import javax.microedition.media.protocol.DataSource;

/** Explicit software-only playback facade; enabled by the shared JVM hook.
 * The original ROM Manager and native libraries are not modified. */
public final class Manager {
    static { System.out.println("J9SIL989 Manager loaded: SILENT playback, no audio hardware"); }
    public static final String TONE_DEVICE_LOCATOR = "device://tone";
    public static final String MIDI_DEVICE_LOCATOR = "device://midi";
    private Manager() {}
    public static String[] getSupportedContentTypes(String protocol) {
        return SilentAudio.types(protocol);
    }
    public static String[] getSupportedProtocols(String type) {
        return SilentAudio.protocols(type);
    }
    public static Player createPlayer(InputStream stream, String type)
            throws IOException, MediaException {
        return SilentAudio.create(stream, type);
    }
    public static Player createPlayer(String locator) throws IOException, MediaException {
        return SilentAudio.create(locator);
    }
    public static Player createPlayer(DataSource source) throws IOException, MediaException {
        return SilentAudio.create(source);
    }
    public static void playTone(int note, int duration, int volume) throws MediaException {
        SilentAudio.playTone(note, duration, volume);
    }
    public static TimeBase getSystemTimeBase() { return SilentAudio.timeBase(); }
}
