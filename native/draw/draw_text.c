#define STB_TRUETYPE_IMPLEMENTATION
#include "../stb_truetype.h"
#include "../draw_common.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAX_FONTS 12

static unsigned char font_data[MAX_FONTS][1 << 25];
static stbtt_fontinfo fonts[MAX_FONTS];
static int font_lens[MAX_FONTS];
static int font_count = 0;

static int utf8_decode(const char *text, int *ci, int *codepoint) {
    unsigned char c = (unsigned char)text[*ci];
    if (c < 0x80) {
        *codepoint = c;
        (*ci)++;
        return 1;
    } else if ((c & 0xE0) == 0xC0) {
        unsigned char c2 = (unsigned char)text[*ci + 1];
        *codepoint = ((c & 0x1F) << 6) | (c2 & 0x3F);
        (*ci) += 2;
        return 2;
    } else if ((c & 0xF0) == 0xE0) {
        unsigned char c2 = (unsigned char)text[*ci + 1];
        unsigned char c3 = (unsigned char)text[*ci + 2];
        *codepoint = ((c & 0x0F) << 12) | ((c2 & 0x3F) << 6) | (c3 & 0x3F);
        (*ci) += 3;
        return 3;
    } else if ((c & 0xF8) == 0xF0) {
        unsigned char c2 = (unsigned char)text[*ci + 1];
        unsigned char c3 = (unsigned char)text[*ci + 2];
        unsigned char c4 = (unsigned char)text[*ci + 3];
        *codepoint = ((c & 0x07) << 18) | ((c2 & 0x3F) << 12) | ((c3 & 0x3F) << 6) | (c4 & 0x3F);
        (*ci) += 4;
        return 4;
    }
    *codepoint = 0;
    (*ci)++;
    return 1;
}

__declspec(dllexport) int Text_LoadFont(const unsigned char *data, int data_len) {
    if (data_len <= 0) return 0;
    // Dedupe: a multi-window batch loads the same font blob once per window,
    // but the pool holds only MAX_FONTS slots.  If this exact blob is already
    // loaded, report success WITHOUT consuming a slot.
    for (int i = 0; i < font_count; i++) {
        if (font_lens[i] == data_len && memcmp(font_data[i], data, (size_t)data_len) == 0) {
            return 1;
        }
    }
    if (font_count >= MAX_FONTS) {
        // MAX_FONTS *distinct* blobs per process; identical blobs are deduped
        // above, so a multi-window batch of the same font never lands here.
        // Each slot is 32 MiB to leave room for large CJK fonts.
        fprintf(stderr, "[Text_LoadFont] font pool full (%d/%d distinct fonts, "
                        "new blob is %d bytes) -- raise MAX_FONTS in draw_text.c\n",
                font_count, MAX_FONTS, data_len);
        return 0;
    }
    if (data_len > (int)sizeof(font_data[font_count])) {
        fprintf(stderr, "[Text_LoadFont] font blob too large: %d > %d bytes\n",
                data_len, (int)sizeof(font_data[font_count]));
        return 0;
    }

    memcpy(font_data[font_count], data, data_len);
    memset(&fonts[font_count], 0, sizeof(stbtt_fontinfo));
    int offset = stbtt_GetFontOffsetForIndex(font_data[font_count], 0);
    if (offset < 0) return 0;
    if (stbtt_InitFont(&fonts[font_count], font_data[font_count], offset)) {
        font_lens[font_count] = data_len;
        font_count++;
        return 1;
    }
    return 0;
}

static int pick_best_font(const char *text) {
    int best = 0;
    int best_score = -1;
    for (int f = 0; f < font_count; f++) {
        int score = 0;
        int ci = 0;
        int len = (int)strlen(text);
        while (ci < len) {
            int cp;
            utf8_decode(text, &ci, &cp);
            if (cp < 32) continue;
            int idx = stbtt_FindGlyphIndex(&fonts[f], cp);
            if (idx != 0) score++;
        }
        if (score > best_score) {
            best_score = score;
            best = f;
        }
    }
    return best;
}

static int get_glyph_font(int codepoint) {
    int first_font = -1;
    for (int f = 0; f < font_count; f++) {
        int idx = stbtt_FindGlyphIndex(&fonts[f], codepoint);
        if (idx != 0) {
            if (first_font < 0) first_font = f;
        }
    }
    return first_font >= 0 ? first_font : 0;
}

static float get_kerning(stbtt_fontinfo *font, int cp1, int cp2, float scale) {
    int g1 = stbtt_FindGlyphIndex(font, cp1);
    int g2 = stbtt_FindGlyphIndex(font, cp2);
    int kern = stbtt_GetGlyphKernAdvance(font, g1, g2);
    return kern * scale;
}

void BuildVerticesFromTexts(const TextObj *texts, int count) {
    if (font_count == 0) return;

    for (int i = 0; i < count; i++) {
        const TextObj *t = &texts[i];
        if (t->text[0] == '\0') continue;

        float base_r = t->r / 255.0f;
        float base_g = t->g / 255.0f;
        float base_b = t->b / 255.0f;

        int best = pick_best_font(t->text);
        float scale = stbtt_ScaleForPixelHeight(&fonts[best], t->font_size);

        int len = (int)strlen(t->text);

        int total_chars = 0;
        { int ci2 = 0; while (ci2 < len) { int cp2; utf8_decode(t->text, &ci2, &cp2); if (cp2 > 32 && cp2 != 10) total_chars++; } }

        float char_progress = t->opacity * (float)total_chars;
        int full_chars = (int)char_progress;
        float frac = char_progress - (float)full_chars;
        if (t->opacity >= 1.0f) { full_chars = total_chars; frac = 0.0f; }
        if (full_chars > total_chars) full_chars = total_chars;

        float text_width = 0;
        int prev_cp = 0;

        int ci = 0;
        while (ci < len) {
            int cp;
            utf8_decode(t->text, &ci, &cp);
            if (cp == 10) { prev_cp = 0; continue; }
            if (cp < 32) { prev_cp = cp; continue; }

            int fi = best;
            int gidx = stbtt_FindGlyphIndex(&fonts[best], cp);
            if (gidx == 0) fi = get_glyph_font(cp);
            float fscale = stbtt_ScaleForPixelHeight(&fonts[fi], t->font_size);

            int adv = 0;
            stbtt_GetCodepointHMetrics(&fonts[fi], cp, &adv, NULL);
            if (adv == 0) {
                stbtt_GetCodepointHMetrics(&fonts[0], cp, &adv, NULL);
            }
            if (cp == 32 && adv == 0) {
                stbtt_GetCodepointHMetrics(&fonts[best], 'x', &adv, NULL);
                if (adv == 0) adv = 1024;
            }
            text_width += adv * fscale;

            if (prev_cp > 32) {
                text_width += get_kerning(&fonts[fi], prev_cp, cp, fscale);
            }
            prev_cp = cp;
        }

        float cursor_x = t->x - text_width * 0.5f;
        float baseline_y = t->y;
        prev_cp = 0;

        int visible_char_idx = 0;
        ci = 0;
        while (ci < len) {
            int cp;
            utf8_decode(t->text, &ci, &cp);

            if (cp == 10) {
                cursor_x = t->x - text_width * 0.5f;
                baseline_y += t->font_size * 1.2f;
                prev_cp = 0;
                continue;
            }
            if (cp < 32) { prev_cp = cp; continue; }

            int fi = best;
            int idx = stbtt_FindGlyphIndex(&fonts[best], cp);
            if (idx == 0) fi = get_glyph_font(cp);
            float fscale = stbtt_ScaleForPixelHeight(&fonts[fi], t->font_size);

            int adv = 0;
            stbtt_GetCodepointHMetrics(&fonts[fi], cp, &adv, NULL);
            if (adv == 0) {
                stbtt_GetCodepointHMetrics(&fonts[0], cp, &adv, NULL);
            }
            if (cp == 32 && adv == 0) {
                stbtt_GetCodepointHMetrics(&fonts[best], 'x', &adv, NULL);
                if (adv == 0) adv = 1024;
            }

            if (prev_cp > 32) {
                cursor_x += get_kerning(&fonts[fi], prev_cp, cp, fscale);
            }

            float char_alpha = 0.0f;
            if (visible_char_idx < full_chars) {
                char_alpha = 1.0f;
            } else if (visible_char_idx == full_chars && frac > 0.0f) {
                char_alpha = frac;
            } else if (t->opacity >= 1.0f) {
                char_alpha = 1.0f;
            }
            visible_char_idx++;

            if (char_alpha > 0.004f) {
                float cr = base_r * char_alpha;
                float cg = base_g * char_alpha;
                float cb = base_b * char_alpha;

                int w = 0, h = 0, xoff = 0, yoff = 0;
                unsigned char *bmp = stbtt_GetCodepointBitmap(&fonts[fi], fscale, fscale, cp, &w, &h, &xoff, &yoff);

            if (bmp && w > 0 && h > 0) {
                float glyph_left = cursor_x + (float)xoff;
                float glyph_top  = baseline_y + (float)yoff;

                for (int row = 0; row < h; row++) {
                    int col = 0;
                    while (col < w) {
                        unsigned char alpha = bmp[row * w + col];
                        if (alpha > 16) {
                            int run_start = col;
                            while (col < w && bmp[row * w + col] > 16) col++;
                            int run_end = col;

                            float x0 = glyph_left + (float)run_start;
                            float y0 = glyph_top  + (float)row;
                            float x1 = glyph_left + (float)run_end;
                            float y1 = y0 + 1.0f;

                            PushVertex(x0, y0, cr, cg, cb, t->alpha);
                            PushVertex(x1, y0, cr, cg, cb, t->alpha);
                            PushVertex(x1, y1, cr, cg, cb, t->alpha);
                            PushVertex(x0, y0, cr, cg, cb, t->alpha);
                            PushVertex(x1, y1, cr, cg, cb, t->alpha);
                            PushVertex(x0, y1, cr, cg, cb, t->alpha);
                        } else {
                            col++;
                        }
                    }
                }
                stbtt_FreeBitmap(bmp, NULL);
            }
            }

            cursor_x += adv * fscale;
            prev_cp = cp;
        }
    }
}
