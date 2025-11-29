import matplotlib.pyplot as plt

_key = None
_fig = None

def _get_current_figure():
    if plt.get_fignums():
        return plt.gcf()
    else:
        return None

def _is_open(fig):
    if fig is None or not isinstance(fig, plt.Figure):
        return False
    return plt.fignum_exists(fig.number)

def _on_key(event):
    global _key, _fig
    _key = event.key
    if _key == 'q':
        plt.close(_fig)
        _fig = None

def _on_close(event):
    global _key, _fig
    _key = 'q'
    _fig = None

def key():
    global _key, _fig
    if _fig is None:
        fig = _get_current_figure()    
        if fig is None:
            return 'q'
        _fig = fig
        _fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)
        _fig.canvas.mpl_connect('key_press_event', _on_key)
        _fig.canvas.mpl_connect("close_event", _on_close)

    else:
        key = _key
        _key = None
        return key
