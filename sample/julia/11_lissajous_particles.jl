include(joinpath(@__DIR__, "py_runtime.jl"))

math = (sqrt=sqrt, sin=sin, cos=cos, tan=tan, asin=asin, acos=acos, atan=atan, atan2=atan, floor=x->Int(floor(x)), ceil=x->Int(ceil(x)), fabs=abs, abs=abs, log=log, log2=log2, log10=log10, exp=exp, pow=(b, e)->b^e, pi=Base.MathConstants.pi, e=Base.MathConstants.e, inf=Inf, nan=NaN)
perf_counter = __pytra_perf_counter
include(joinpath(@__DIR__, "utils", "gif.jl"))

# 11: Sample that outputs Lissajous-motion particles as a GIF.

function color_palette()
    p = UInt8[]
    for i in 0:256 - 1
        r = i
        g = ((i * 3) % 256)
        b = (255 - i)
        push!(p, r)
        push!(p, g)
        push!(p, b)
    end
    return __pytra_bytes(p)
end

function run_11_lissajous_particles()
    w = 320
    h = 240
    frames_n = 360
    particles = 48
    out_path = "sample/out/11_lissajous_particles.gif"
    
    start = perf_counter()
    frames = Any[]
    
    for t in 0:frames_n - 1
        frame = __pytra_bytearray((w * h))
        
        for p in 0:particles - 1
            phase = (p * 0.261799)
            x = __pytra_int(((w * 0.5) + ((w * 0.38) * math.sin(((0.11 * t) + (phase * 2.0))))))
            y = __pytra_int(((h * 0.5) + ((h * 0.38) * math.sin(((0.17 * t) + (phase * 3.0))))))
            color = (30 + ((p * 9) % 220))
            
            for dy in (-2):3 - 1
                for dx in (-2):3 - 1
                    xx = (x + dx)
                    yy = (y + dy)
                    if ((xx >= 0) && (xx < w) && (yy >= 0) && (yy < h))
                        d2 = ((dx * dx) + (dy * dy))
                        if (d2 <= 4)
                            idx = ((yy * w) + xx)
                            v = (color - (d2 * 20))
                            v = max(0, v)
                            if (v > frame[__pytra_idx(idx, length(frame))])
                                frame[__pytra_idx(idx, length(frame))] = v
                            end
                        end
                    end
                end
            end
        end
        push!(frames, __pytra_bytes(frame))
    end
    save_gif(out_path, w, h, frames, color_palette(), 3, 0)
    elapsed = (perf_counter() - start)
    __pytra_print("output:", out_path)
    __pytra_print("frames:", frames_n)
    __pytra_print("elapsed_sec:", elapsed)
end


run_11_lissajous_particles()
