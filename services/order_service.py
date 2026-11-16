"""Order service - business logic for order operations."""

from models.order import Order


class OrderService:
    # Order status flow
    STATUS_FLOW = ['Pending', 'Confirmed', 'Processing', 'Shipped', 'Delivered']
    
    @staticmethod
    def get_status_index(status):
        """Get the index of a status in the flow."""
        try:
            return OrderService.STATUS_FLOW.index(status)
        except ValueError:
            return -1
    
    @staticmethod
    def get_tracking_steps(status):
        """Get tracking steps with their completion state."""
        steps = []
        current_index = OrderService.get_status_index(status)
        
        for i, step in enumerate(OrderService.STATUS_FLOW):
            steps.append({
                'name': step,
                'completed': i <= current_index,
                'current': i == current_index,
                'index': i
            })
        
        return steps
    
    @staticmethod
    def can_cancel(order):
        """Check if an order can be cancelled."""
        return order['status'] in ('Pending', 'Confirmed')
