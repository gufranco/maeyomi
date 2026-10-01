class Maeyomi < Formula
  include Language::Python::Virtualenv

  desc "Print playable cards for Barcode Battler machines and barcode games"
  homepage "https://github.com/gufranco/maeyomi"
  url "https://github.com/gufranco/maeyomi/archive/refs/tags/v1.19.0.tar.gz"
  sha256 "f02b8ee6a699600fd5c56d5a792469b298a938d27d2529911c1aaa8d5738723a"
  license "MIT"
  head "https://github.com/gufranco/maeyomi.git", branch: "main"

  depends_on "uv" => :build
  depends_on "python@3.14"

  def install
    python = formula_opt_bin("python@3.14")/"python3.14"
    ENV["UV_PROJECT_ENVIRONMENT"] = libexec
    ENV["UV_PYTHON_DOWNLOADS"] = "never"
    system "uv", "sync", "--frozen", "--no-dev", "--no-editable", "--extra", "ui",
           "--python", python
    bin.install_symlink libexec/"bin/maeyomi"
    sign_native_libraries if OS.mac?
  end

  def sign_native_libraries
    Dir[libexec/"lib/**/*.{so,dylib}"].each do |path|
      library = Pathname(path)
      if library.dylib?
        MachO::Tools.change_dylib_id(library, (opt_libexec/library.relative_path_from(libexec)).to_s)
      end
      next if quiet_system "codesign", "--verify", library

      system "codesign", "--force", "--sign", "-", library
    end
  end

  test do
    assert_match "maeyomi", shell_output("#{bin}/maeyomi --help")

    system bin/"maeyomi", "doctor"

    system bin/"maeyomi", "decode", "4902102072618"

    system bin/"maeyomi", "random", "--count", "1", "--seed", "1", "--output", testpath/"card.pdf"
    assert_path_exists testpath/"card.pdf"
  end
end
