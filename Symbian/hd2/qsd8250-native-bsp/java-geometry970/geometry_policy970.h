#ifndef GEOMETRY_POLICY970_H
#define GEOMETRY_POLICY970_H

// Only the HD2 portrait nominal-to-physical mismatch. No app identity is used.
// Exact equality avoids double conversion and leaves unknown modes untouched.
inline bool Geometry970NominalSize(int width, int height, int panelWidth,
    int panelHeight, int xResult, int yResult, bool portrait)
    {
    return portrait && xResult == 0 && yResult == 0 &&
        width == 360 && height == 640 &&
        panelWidth == 480 && panelHeight == 800;
    }

inline bool Geometry970NominalRect(int left, int top, int right, int bottom,
    int panelWidth, int panelHeight, int xResult, int yResult, bool portrait)
    {
    return left == 0 && top == 0 && Geometry970NominalSize(right, bottom,
        panelWidth, panelHeight, xResult, yResult, portrait);
    }
#endif
