package com.hd2.media;

import java.util.Vector;
import javax.microedition.media.MediaException;

/** Header/event parser only. It does not claim to decode or produce audio. */
public final class AudioDuration {
    private AudioDuration() {}
    private static void need(boolean ok) throws MediaException {
        if (!ok) throw new MediaException("Silent playback: malformed or unsupported finite audio");
    }
    private static boolean tag(byte[] b, int p, String s) {
        if (p < 0 || p > b.length - s.length()) return false;
        for (int i=0; i<s.length(); ++i) if ((b[p+i]&255) != s.charAt(i)) return false;
        return true;
    }
    private static int be16(byte[] b, int p) { return ((b[p]&255)<<8) | (b[p+1]&255); }
    private static long be32(byte[] b, int p) { return ((long)be16(b,p)<<16) | be16(b,p+2); }
    private static int le16(byte[] b, int p) { return (b[p]&255) | ((b[p+1]&255)<<8); }
    private static long le32(byte[] b, int p) { return le16(b,p) | ((long)le16(b,p+2)<<16); }
    public static String detect(byte[] b) throws MediaException {
        if (tag(b,0,"RIFF")) return "audio/x-wav";
        if (tag(b,0,"MThd")) return "audio/midi";
        if (tag(b,0,"ID3") || (b.length>=2 && (b[0]&255)==255 && (b[1]&224)==224)) return "audio/mpeg";
        throw new MediaException("Silent playback: unknown audio format");
    }
    public static long measure(byte[] b, String type) throws MediaException {
        need(type != null);
        if (type.equals("audio/x-wav")) return wav(b);
        if (type.equals("audio/mpeg")) return mpeg(b);
        if (type.equals("audio/midi")) return midi(b);
        throw new MediaException("Silent playback: unsupported format");
    }
    private static long wav(byte[] b) throws MediaException {
        need(b.length>=12 && tag(b,0,"RIFF") && tag(b,8,"WAVE"));
        long end=8+le32(b,4); need(end<=b.length && end>=12);
        int p=12, align=0, channels=0, bits=0; long rate=0, bytes=0; boolean data=false;
        while (p+8<=end) {
            long size=le32(b,p+4); need(size<=end-p-8);
            int at=p+8;
            if (tag(b,p,"fmt ")) {
                need(size>=16 && le16(b,at)==1); // PCM only, not an invented codec.
                channels=le16(b,at+2); rate=le32(b,at+4); align=le16(b,at+12); bits=le16(b,at+14);
                need(channels>0 && channels<=8 && rate>0 && rate<=384000 && bits>0 && bits<=32 && bits%8==0);
                need(align==channels*(bits/8) && le32(b,at+8)==rate*align);
            } else if (tag(b,p,"data")) { bytes+=size; data=true; }
            p=at+(int)size+((int)size&1);
        }
        need(p==end && align>0 && data && bytes%align==0);
        return (bytes/align)*1000000L/rate;
    }
    private static final int[] M1L1={0,32,64,96,128,160,192,224,256,288,320,352,384,416,448};
    private static final int[] M1L2={0,32,48,56,64,80,96,112,128,160,192,224,256,320,384};
    private static final int[] M1L3={0,32,40,48,56,64,80,96,112,128,160,192,224,256,320};
    private static final int[] M2L1={0,32,48,56,64,80,96,112,128,144,160,176,192,224,256};
    private static final int[] M2LX={0,8,16,24,32,40,48,56,64,80,96,112,128,144,160};
    private static long mpeg(byte[] b) throws MediaException {
        int p=0, frames=0; long ns=0;
        if (tag(b,0,"ID3")) {
            need(b.length>=10 && (b[3]==3 || b[3]==4 || b[3]==2));
            int size=0; for(int i=6;i<10;i++){need((b[i]&128)==0);size=(size<<7)|(b[i]&127);}
            p=10+size+((b[3]==4 && (b[5]&16)!=0)?10:0); need(p<=b.length);
        }
        while(p<b.length) {
            if(b.length-p==128 && tag(b,p,"TAG")) {p=b.length;break;}
            if(b[p]==0) {while(p<b.length && b[p]==0)++p;need(p==b.length);break;}
            need(p+4<=b.length && (b[p]&255)==255 && (b[p+1]&224)==224);
            int version=(b[p+1]>>3)&3, layer=(b[p+1]>>1)&3, bi=(b[p+2]>>4)&15, ri=(b[p+2]>>2)&3;
            need(version!=1 && layer!=0 && bi!=0 && bi!=15 && ri!=3);
            int rate=(ri==0?44100:ri==1?48000:32000)/(version==3?1:version==2?2:4);
            int[] table=version==3?(layer==3?M1L1:layer==2?M1L2:M1L3):(layer==3?M2L1:M2LX);
            int bitrate=table[bi]*1000, pad=(b[p+2]>>1)&1;
            int samples=layer==3?384:layer==1&&version!=3?576:1152;
            int size=layer==3?(12*bitrate/rate+pad)*4:(layer==1&&version!=3?72:144)*bitrate/rate+pad;
            need(size>=4 && size<=b.length-p); p+=size; ++frames;
            ns+=samples*1000000000L/rate;
        }
        need(frames>0 && p==b.length); return ns/1000L;
    }
    private static long vlq(byte[] b, int[] cursor, int end) throws MediaException {
        long n=0; for(int i=0;i<4;i++) {need(cursor[0]<end);int v=b[cursor[0]++]&255;n=(n<<7)|(v&127);if(v<128)return n;}
        throw new MediaException("Silent playback: invalid MIDI VLQ");
    }
    private static long midi(byte[] b) throws MediaException {
        need(b.length>=14 && tag(b,0,"MThd") && be32(b,4)==6);
        int format=be16(b,8), tracks=be16(b,10), division=be16(b,12), p=14, events=0;
        need(format<=1 && tracks>0 && tracks<=128 && (format!=0 || tracks==1) && division!=0);
        long endTick=0; Vector tempos=new Vector();
        for(int tr=0;tr<tracks;tr++) {
            need(p+8<=b.length && tag(b,p,"MTrk")); long length=be32(b,p+4);need(length<=b.length-p-8);
            int end=p+8+(int)length;int[] cursor={p+8}; int running=0;long tick=0;boolean ended=false;
            while(cursor[0]<end) {
                need(++events<=250000);tick+=vlq(b,cursor,end);need(cursor[0]<end);
                int status=b[cursor[0]]&255;
                if(status>=128) ++cursor[0]; else {need(running>=128 && running<240);status=running;}
                if(status<240) {
                    running=status;int n=(status&240)==192||(status&240)==208?1:2;
                    need(n<=end-cursor[0]);for(int i=0;i<n;i++)need((b[cursor[0]++]&128)==0);
                } else if(status==255) {
                    need(cursor[0]<end);int kind=b[cursor[0]++]&255;long size=vlq(b,cursor,end);need(size<=end-cursor[0]);
                    if(kind==81) {
                        need(size==3 && tempos.size()<10000);int q=cursor[0];long tempo=((long)(b[q]&255)<<16)|be16(b,q+1);need(tempo>0);
                        int at=tempos.size();while(at>0 && ((long[])tempos.elementAt(at-1))[0]>tick)--at;
                        tempos.insertElementAt(new long[]{tick,tempo},at);
                    }
                    cursor[0]+=(int)size;
                    if(kind==47) {need(size==0 && cursor[0]==end);ended=true;break;}
                } else if(status==240||status==247) {
                    running=0;long size=vlq(b,cursor,end);need(size<=end-cursor[0]);cursor[0]+=(int)size;
                } else need(false);
            }
            need(ended);if(tick>endTick)endTick=tick;p=end;
        }
        need(p==b.length);
        if((division&32768)!=0) {
            int fps=256-(division>>8), resolution=division&255;need(resolution>0&&(fps==24||fps==25||fps==29||fps==30));
            need(endTick <= Long.MAX_VALUE / (fps==29 ? 1001000000L : 1000000L));
            return fps==29?endTick*1000000L*1001L/(30000L*resolution):endTick*1000000L/(fps*resolution);
        }
        long tick=0, weighted=0, tempo=500000;
        for(int i=0;i<tempos.size();i++) {
            long[] t=(long[])tempos.elementAt(i);
            need(t[0]<=endTick && (t[0]-tick)<=Long.MAX_VALUE/tempo);
            long part=(t[0]-tick)*tempo;need(part<=Long.MAX_VALUE-weighted);weighted+=part;tick=t[0];tempo=t[1];
        }
        need(endTick-tick<=Long.MAX_VALUE/tempo);
        long tail=(endTick-tick)*tempo;need(tail<=Long.MAX_VALUE-weighted);
        return (weighted+tail)/division;
    }
}
