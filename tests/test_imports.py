def test_package_imports() -> None:
    import davinci_resolve_mcp
    from davinci_resolve_mcp.resolve_api import ResolveAPI

    assert davinci_resolve_mcp.__version__
    assert ResolveAPI is not None
