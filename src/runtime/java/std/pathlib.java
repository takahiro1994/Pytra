// Hand-written pathlib.Path for Java runtime.
// Provides minimal Path operations needed by sample programs.

import java.nio.file.Files;
import java.nio.file.Paths;

public final class pathlib {
    private pathlib() {
    }

    public static Path Path() {
        return new Path();
    }

    public static Path Path(String p) {
        return new Path(p);
    }

    public static Path Path(Path other) {
        return new Path(other);
    }

    public static class Path {
        public String _path;

        public Path() {
            this._path = "";
        }

        public Path(String p) {
            this._path = p;
        }

        public Path(Path other) {
            this._path = other._path;
        }

        public String toString() {
            return _path;
        }

        public String __repr__() {
            return "Path('" + _path + "')";
        }

        public String __fspath__() {
            return _path;
        }

        public Path __truediv__(String other) {
            if (_path.equals("") || _path.equals(".")) {
                return new Path(other);
            }
            return new Path(_path + "/" + other);
        }

        public Path joinpath(String other) {
            return __truediv__(other);
        }

        public Path joinpath(String first, String second) {
            return __truediv__(first).__truediv__(second);
        }

        public Path parent() {
            java.nio.file.Path p = Paths.get(_path).getParent();
            if (p == null) {
                return new Path(".");
            }
            return new Path(p.toString());
        }

        public String name() {
            java.nio.file.Path p = Paths.get(_path).getFileName();
            if (p == null) {
                return "";
            }
            return p.toString();
        }

        public String suffix() {
            String n = name();
            int dot = n.lastIndexOf('.');
            if (dot <= 0) {
                return "";
            }
            return n.substring(dot);
        }

        public String stem() {
            String n = name();
            int dot = n.lastIndexOf('.');
            if (dot <= 0) {
                return n;
            }
            return n.substring(0, dot);
        }

        public boolean exists() {
            return Files.exists(Paths.get(_path));
        }

        public void mkdir(boolean parents, boolean exist_ok) {
            try {
                java.nio.file.Path p = Paths.get(_path);
                if (parents) {
                    Files.createDirectories(p);
                } else {
                    Files.createDirectory(p);
                }
            } catch (java.nio.file.FileAlreadyExistsException e) {
                if (!exist_ok) {
                    throw new RuntimeException(e);
                }
            } catch (java.io.IOException e) {
                throw new RuntimeException(e);
            }
        }

        public void mkdir() {
            mkdir(false, false);
        }

        public String read_text(String encoding) {
            try {
                return new String(Files.readAllBytes(Paths.get(_path)), encoding);
            } catch (java.io.IOException e) {
                throw new RuntimeException(e);
            }
        }

        public String read_text() {
            return read_text("UTF-8");
        }

        public void write_text(String content, String encoding) {
            try {
                java.nio.file.Path path = Paths.get(_path);
                java.nio.file.Path parent = path.getParent();
                if (parent != null) {
                    Files.createDirectories(parent);
                }
                Files.write(path, content.getBytes(encoding));
            } catch (java.io.IOException e) {
                throw new RuntimeException(e);
            }
        }

        public void write_text(String content) {
            write_text(content, "UTF-8");
        }
    }
}
