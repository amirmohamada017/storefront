from django.dispatch import receiver
from store.signals import order_created


@receiver(order_created)
def on_order_created(sender, **kwargs):
    order = kwargs['order']


order_created.connect(on_order_created)
