def test_scss_loading():
    from oscad._scss import OscadScssCompiler

    compiler = OscadScssCompiler(['oscad:assets/scss/'])
    compiled = compiler.compile_from_path('bootstrap', 'icons')
    assert compiled is not None
    assert '@import' not in compiled
