# Integer promotion: cross-size assignment, mixed arithmetic, sign extension.


def _case_main() -> None:
    # --- size widening assignment ---
    a8: int8 = 42
    a16: int16 = a8
    print(a16)  # 42

    b16: int16 = 1000
    b32: int32 = b16
    print(b32)  # 1000

    c32: int32 = 100000
    c64: int64 = c32
    print(c64)  # 100000

    # --- unsigned widening ---
    u8: uint8 = 255
    u16: uint16 = u8
    print(u16)  # 255

    u16b: uint16 = 65535
    u32: uint32 = u16b
    print(u32)  # 65535

    # --- negative sign extension ---
    neg8: int8 = -1
    neg16: int16 = neg8
    print(neg16)  # -1

    neg16b: int16 = -128
    neg32: int32 = neg16b
    print(neg32)  # -128

    neg32b: int32 = -100000
    neg64: int64 = neg32b
    print(neg64)  # -100000

    # --- unsigned to signed widening ---
    us8: uint8 = 200
    us16: int16 = us8
    print(us16)  # 200

    us16b: uint16 = 50000
    us32: int32 = us16b
    print(us32)  # 50000

    # --- mixed arithmetic (different sizes) ---
    x8: int8 = 10
    x16: int16 = 20
    r1: int16 = x8 + x16
    print(r1)  # 30

    y16: int16 = 100
    y32: int32 = 200
    r2: int32 = y16 + y32
    print(r2)  # 300

    z32: int32 = 1000
    z64: int64 = 2000
    r3: int64 = z32 + z64
    print(r3)  # 3000

    # --- mixed arithmetic (signed + unsigned) ---
    s8: int8 = -10
    u8b: uint8 = 20
    r4: int16 = s8 + u8b
    print(r4)  # 10

    # --- multiplication promotion ---
    m8: int8 = 100
    m16: int16 = 100
    r5: int32 = m8 * m16
    print(r5)  # 10000

    # --- negative multiplication ---
    n8: int8 = -5
    n16: int16 = 3
    r6: int16 = n8 * n16
    print(r6)  # -15

    # --- int8 boundary values ---
    max8: int8 = 127
    min8: int8 = -128
    max8_wide: int16 = max8
    min8_wide: int16 = min8
    print(max8_wide)   # 127
    print(min8_wide)   # -128

    # --- uint8 boundary ---
    maxu8: uint8 = 255
    maxu8_wide: int16 = maxu8
    print(maxu8_wide)  # 255

    # --- int16 boundary values ---
    max16: int16 = 32767
    min16: int16 = -32768
    max16_wide: int32 = max16
    min16_wide: int32 = min16
    print(max16_wide)  # 32767
    print(min16_wide)  # -32768


if __name__ == "__main__":
    _case_main()
