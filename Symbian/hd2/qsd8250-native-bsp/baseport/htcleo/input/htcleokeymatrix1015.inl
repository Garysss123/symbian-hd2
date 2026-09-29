#ifndef HTCLEO_KEYMATRIX_1015
#define HTCLEO_KEYMATRIX_1015
// Matrix(1,2) and GPIO94 report the same physical End/Power button.
static inline unsigned HtcleoMergePower1015(unsigned matrix, bool powerDown) {
    return matrix | (powerDown ? (1u<<5) : 0u);
}
static inline bool HtcleoKeyMuxResult1015(int result) {
    // MAGLDR retains the board mux; only the known unavailable modem timeout
    // is tolerated. Bad arguments and other actual errors remain failures.
    return result==0 || result==-33; // KErrNone, KErrTimedOut
}
#endif
