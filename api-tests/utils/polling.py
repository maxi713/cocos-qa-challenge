import polling2


def wait_for_order_resolution(orders_service, order_id, timeout=2):
    def get_order():
        orders = orders_service.get_orders().body
        return next(o for o in orders if o["id"] == order_id)

    return polling2.poll(
        get_order,
        check_success=lambda order: order["status"] != "PENDING",
        step=0.2,
        timeout=timeout,
    )
