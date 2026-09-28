class Maeyomi < Formula
  include Language::Python::Virtualenv

  desc "Print playable cards for Barcode Battler machines and barcode games"
  homepage "https://github.com/gufranco/maeyomi"
  url "https://github.com/gufranco/maeyomi/archive/refs/tags/v1.1.0.tar.gz"
  sha256 "4ec486e4e34230a1ba2a527e167a6d2a9683c404914deeecbb3c4be5bcf3a356"
  license "MIT"
  head "https://github.com/gufranco/maeyomi.git", branch: "main"

  depends_on "python@3.14"
  depends_on "uv" => :build

  def install
    python = Formula["python@3.14"].opt_bin/"python3.14"
    ENV["UV_PROJECT_ENVIRONMENT"] = libexec
    ENV["UV_PYTHON_DOWNLOADS"] = "never"
    system "uv", "sync", "--frozen", "--no-dev", "--no-editable", "--extra", "ui",
           "--python", python
    bin.install_symlink libexec/"bin/maeyomi"
  end

  test do
    assert_match "maeyomi", shell_output("#{bin}/maeyomi --help")

    system bin/"maeyomi", "doctor"

    system bin/"maeyomi", "decode", "4902102072618"

    system bin/"maeyomi", "random", "--count", "1", "--seed", "1", "--output", testpath/"card.pdf"
    assert_predicate testpath/"card.pdf", :exist?
  end
end
