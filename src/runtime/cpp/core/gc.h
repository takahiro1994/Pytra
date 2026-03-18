// このファイルは `src/gc.h` のテスト/実装コードです。
// 読み手が責務を把握しやすいように、日本語コメントを追記しています。
// 変更時は、スレッド安全性と参照カウント整合性を必ず確認してください。

#ifndef PYTRA_BUILT_IN_GC_H
#define PYTRA_BUILT_IN_GC_H

#include <atomic>
#include <cassert>
#include <cstdint>
#include <optional>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>

namespace pytra::gc {

template <class T>
class RcHandle;
class RcObject;

class RcObject {
public:
    RcObject() : ref_count_(1) {}
    RcObject(const RcObject&) noexcept : ref_count_(1) {}
    RcObject(RcObject&&) noexcept : ref_count_(1) {}
    RcObject& operator=(const RcObject&) noexcept {
        ref_count_.store(1, ::std::memory_order_release);
        return *this;
    }
    RcObject& operator=(RcObject&&) noexcept {
        ref_count_.store(1, ::std::memory_order_release);
        return *this;
    }
    virtual ~RcObject() = default;

    uint32_t ref_count() const noexcept {
        return ref_count_.load(::std::memory_order_acquire);
    }

    virtual void rc_release_refs();

    virtual uint32_t py_type_id() const noexcept { return 0; }

    // Iterator protocol: default implementations throw; subclasses override to support iteration.
    // Declared with forward-declared RcHandle; definitions provided inline after RcHandle.
    virtual RcHandle<RcObject> py_iter_or_raise() const;
    virtual ::std::optional<RcHandle<RcObject>> py_next_or_stop();
    // py_truthy: default false; subclasses override
    virtual bool py_truthy() const { return true; }

private:
    template <class U>
    friend class RcHandle;
    friend void incref(RcObject* obj) noexcept;
    friend void decref(RcObject* obj) noexcept;

    ::std::atomic<uint32_t> ref_count_;
};


void incref(RcObject* obj) noexcept;
void decref(RcObject* obj) noexcept;

/**
 * @brief RC管理オブジェクトを生成します。
 *
 * @tparam T 生成するクラス（RcObject 継承必須）
 * @tparam Args コンストラクタ引数型
 * @param args T のコンストラクタへ渡す引数
 * @return T* 生成したオブジェクト（初期 ref_count=1）
 */
template <class T, class... Args>
T* rc_new(Args&&... args) {
    static_assert(::std::is_base_of_v<RcObject, T>, "T must derive from RcObject");
    return new T(::std::forward<Args>(args)...);
}

template <class T>
class RcHandle {
public:
    template <class U>
    using EnableUpcast = ::std::enable_if_t<
        ::std::is_base_of_v<RcObject, U> &&
        ::std::is_convertible_v<U*, T*> &&
        !::std::is_same_v<U, T>,
        int>;

    RcHandle() = default;

    explicit RcHandle(T* ptr, bool add_ref = true) : ptr_(ptr) {
        static_assert(::std::is_base_of_v<RcObject, T>, "T must derive from RcObject");
        if (ptr_ != nullptr && add_ref) {
            incref(reinterpret_cast<RcObject*>(ptr_));
        }
    }

    /**
     * @brief rc_new 直後の裸ポインタをそのまま所有するファクトリです。
     * @param ptr 所有開始するポインタ（追加 incref しない）
     */
    static RcHandle<T> adopt(T* ptr) {
        RcHandle<T> h;
        h.ptr_ = ptr;
        return h;
    }

    RcHandle(const RcHandle& other) : ptr_(other.ptr_) {
        if (ptr_ != nullptr) {
            incref(reinterpret_cast<RcObject*>(ptr_));
        }
    }

    RcHandle(RcHandle&& other) noexcept : ptr_(other.ptr_) {
        other.ptr_ = nullptr;
    }

    template <class U, EnableUpcast<U> = 0>
    RcHandle(const RcHandle<U>& other) : ptr_(static_cast<T*>(other.get())) {
        if (ptr_ != nullptr) {
            incref(reinterpret_cast<RcObject*>(ptr_));
        }
    }

    template <class U, EnableUpcast<U> = 0>
    RcHandle(RcHandle<U>&& other) noexcept : ptr_(static_cast<T*>(other.release())) {}

    RcHandle& operator=(const RcHandle& other) {
        if (this == &other) {
            return *this;
        }
        reset(other.ptr_);
        return *this;
    }

    RcHandle& operator=(RcHandle&& other) noexcept {
        if (this == &other) {
            return *this;
        }
        if (ptr_ != nullptr) {
            decref(reinterpret_cast<RcObject*>(ptr_));
        }
        ptr_ = other.ptr_;
        other.ptr_ = nullptr;
        return *this;
    }

    template <class U, EnableUpcast<U> = 0>
    RcHandle& operator=(const RcHandle<U>& other) {
        reset(static_cast<T*>(other.get()));
        return *this;
    }

    template <class U, EnableUpcast<U> = 0>
    RcHandle& operator=(RcHandle<U>&& other) noexcept {
        if (ptr_ != nullptr) {
            decref(reinterpret_cast<RcObject*>(ptr_));
        }
        ptr_ = static_cast<T*>(other.release());
        return *this;
    }

    ~RcHandle() {
        if (ptr_ != nullptr) {
            decref(reinterpret_cast<RcObject*>(ptr_));
            ptr_ = nullptr;
        }
    }

    /**
     * @brief 保持対象を差し替えます。
     *
     * @param ptr 新たに保持するポインタ
     * @param add_ref true の場合、差し替え前に incref します
     */
    void reset(T* ptr = nullptr, bool add_ref = true) {
        if (ptr != nullptr && add_ref) {
            incref(reinterpret_cast<RcObject*>(ptr));
        }
        if (ptr_ != nullptr) {
            decref(reinterpret_cast<RcObject*>(ptr_));
        }
        ptr_ = ptr;
    }

    T* release() noexcept {
        T* out = ptr_;
        ptr_ = nullptr;
        return out;
    }

    T* get() const noexcept { return ptr_; }
    T& operator*() const noexcept { return *ptr_; }
    T* operator->() const noexcept { return ptr_; }
    explicit operator bool() const noexcept { return ptr_ != nullptr; }
    bool operator==(const RcHandle& other) const noexcept { return ptr_ == other.ptr_; }
    bool operator!=(const RcHandle& other) const noexcept { return ptr_ != other.ptr_; }

private:
    T* ptr_ = nullptr;
};

}  // namespace pytra::gc

#endif  // PYTRA_BUILT_IN_GC_H
