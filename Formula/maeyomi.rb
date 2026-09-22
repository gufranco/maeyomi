class Maeyomi < Formula
  include Language::Python::Virtualenv

  desc "Print playable cards for a 1992 Epoch Barcode Battler II"
  homepage "https://github.com/gufranco/maeyomi"
  url "https://github.com/gufranco/maeyomi/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "35d221880bae92ff6a4e3bffa0a2763b3ebfc98c2019b4fb0c7e2f5cb3f361fd"
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
