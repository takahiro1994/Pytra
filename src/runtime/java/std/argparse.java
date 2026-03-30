import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public final class argparse {
    private argparse() {
    }

    public static ArgumentParser ArgumentParser(String description) {
        return new ArgumentParser(description);
    }

    public static final class ArgumentParser {
        private static final class ArgSpec {
            public ArrayList<String> names = new ArrayList<>();
            public String action = "";
            public ArrayList<String> choices = new ArrayList<>();
            public Object defaultValue = null;
            public boolean isOptional = false;
            public String dest = "";
        }

        public String description;
        private final ArrayList<ArgSpec> specs = new ArrayList<>();

        public ArgumentParser() {
            this("");
        }

        public ArgumentParser(String description) {
            this.description = description;
        }

        public void add_argument(Object... params) {
            ArgSpec spec = new ArgSpec();
            for (Object param : params) {
                if (param instanceof String) {
                    String text = (String) param;
                    if (text.equals("store_true") || text.equals("store_false")) {
                        spec.action = text;
                    } else if (text.startsWith("-")) {
                        spec.names.add(text);
                    } else if (spec.names.isEmpty()) {
                        spec.names.add(text);
                    } else {
                        spec.defaultValue = text;
                    }
                    continue;
                }
                if (param instanceof ArrayList<?>) {
                    for (Object item : (ArrayList<?>) param) {
                        spec.choices.add(PyRuntime.pyToString(item));
                    }
                    continue;
                }
                if (param != null) {
                    spec.defaultValue = param;
                }
            }
            if (spec.names.isEmpty()) {
                throw new RuntimeException("add_argument requires at least one name");
            }
            spec.isOptional = spec.names.get(0).startsWith("-");
            if (spec.isOptional) {
                spec.dest = spec.names.get(spec.names.size() - 1).replaceFirst("^-+", "").replace("-", "_");
            } else {
                spec.dest = spec.names.get(0);
            }
            if (spec.action.equals("store_true") && spec.defaultValue == null) {
                spec.defaultValue = false;
            }
            specs.add(spec);
        }

        public HashMap<String, Object> parse_args() {
            ArrayList<String> argv = new ArrayList<>();
            int i = 1;
            while (i < PyRuntime.__pytra_argv.size()) {
                argv.add(PyRuntime.__pytra_argv.get(i));
                i += 1;
            }
            return parse_args(argv);
        }

        public HashMap<String, Object> parse_args(List<String> argv) {
            ArrayList<ArgSpec> positional = new ArrayList<>();
            ArrayList<ArgSpec> optional = new ArrayList<>();
            for (ArgSpec spec : specs) {
                if (spec.isOptional) {
                    optional.add(spec);
                } else {
                    positional.add(spec);
                }
            }

            HashMap<String, Integer> byName = new HashMap<>();
            int index = 0;
            for (ArgSpec spec : optional) {
                for (String name : spec.names) {
                    byName.put(name, index);
                }
                index += 1;
            }

            HashMap<String, Object> values = new HashMap<>();
            for (ArgSpec spec : specs) {
                if (spec.action.equals("store_true")) {
                    values.put(spec.dest, spec.defaultValue instanceof Boolean ? spec.defaultValue : false);
                } else if (spec.defaultValue != null) {
                    values.put(spec.dest, spec.defaultValue);
                } else {
                    values.put(spec.dest, null);
                }
            }

            int posIndex = 0;
            int i = 0;
            while (i < argv.size()) {
                String tok = argv.get(i);
                if (tok.startsWith("-")) {
                    Integer specIndex = byName.get(tok);
                    if (specIndex == null) {
                        throw new RuntimeException("unknown option: " + tok);
                    }
                    ArgSpec spec = optional.get(specIndex.intValue());
                    if (spec.action.equals("store_true")) {
                        values.put(spec.dest, true);
                        i += 1;
                        continue;
                    }
                    if (i + 1 >= argv.size()) {
                        throw new RuntimeException("missing value for option: " + tok);
                    }
                    String value = argv.get(i + 1);
                    if (!spec.choices.isEmpty() && !spec.choices.contains(value)) {
                        throw new RuntimeException("invalid choice for " + tok + ": " + value);
                    }
                    values.put(spec.dest, value);
                    i += 2;
                    continue;
                }
                if (posIndex >= positional.size()) {
                    throw new RuntimeException("unexpected extra argument: " + tok);
                }
                ArgSpec spec = positional.get(posIndex);
                values.put(spec.dest, tok);
                posIndex += 1;
                i += 1;
            }
            if (posIndex < positional.size()) {
                throw new RuntimeException("missing required argument: " + positional.get(posIndex).dest);
            }
            return values;
        }
    }
}
