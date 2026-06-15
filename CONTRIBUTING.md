# Contributing / Đóng góp

Thank you for your interest in contributing! 🎉

## How to Contribute

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Commit** your changes: `git commit -m "Add your feature"`
4. **Push** to the branch: `git push origin feature/your-feature`
5. **Open** a Pull Request

## Guidelines

- Keep code clean and readable
- Follow existing code style (PEP 8)
- Test your changes before submitting
- Add comments for complex logic
- Update `README.md` if you add new features

## Reporting Bugs

Open an [Issue](../../issues) with:
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS

## Adding New TLDs

To add support for a new TLD:
1. Find the RDAP endpoint for the TLD (check [IANA RDAP Bootstrap](https://data.iana.org/rdap/dns.json))
2. Add the endpoint to `RDAP_ENDPOINTS` dict in `main.py`
3. Add the TLD to `TLD_OPTIONS` list
4. Test with a few domains

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
