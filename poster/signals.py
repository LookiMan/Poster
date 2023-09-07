from django.dispatch import Signal


publish_post_signal = Signal(use_caching=True)
unpublish_post_signal = Signal(use_caching=True)

edit_post_signal = Signal(use_caching=True)
