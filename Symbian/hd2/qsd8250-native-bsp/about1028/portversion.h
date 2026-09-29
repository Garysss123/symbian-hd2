// Bounded ASCII package-field parser shared by device code and host tests.
#ifndef HTCLEO_ABOUT1028_PORTVERSION_H
#define HTCLEO_ABOUT1028_PORTVERSION_H
inline int AboutBuild1028(const unsigned char* bytes, int size, char* out, int cap)
    {
    if (!bytes || !out || size < 0 || size > 4096 || cap < 2) return 0;
    const char key[] = "Package: ";
    int found = 0, count = 0;
    for (int i = 0; i < size; ++i)
        {
        if (i && bytes[i-1] != '\n') continue;
        int k = 0;
        while (k < 9 && i+k < size && bytes[i+k] == (unsigned char)key[k]) ++k;
        if (k != 9) continue;
        if (++found != 1) return 0;
        int j = i+9;
        while (j < size && bytes[j] >= '0' && bytes[j] <= '9')
            {
            if (count >= cap-1 || count >= 6) return 0;
            out[count++] = (char)bytes[j++];
            }
        const char suffix[] = "-symbian3-";
        for (k = 0; k < 10; ++k)
            if (j+k >= size || bytes[j+k] != (unsigned char)suffix[k]) return 0;
        }
    if (found != 1 || !count) return 0;
    out[count] = 0;
    return count;
    }
#endif
