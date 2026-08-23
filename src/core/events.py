"""
Core Event Bus for Real-Time Decoupled Communication
"""
import logging
from typing import Any, Callable, Dict, List
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


class EventBus:
    """In-memory Event Bus for decoupled module communication."""
    
    _instance = None
    _listeners: Dict[str, List[Callable]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
        return cls._instance

    @classmethod
    def subscribe(cls, event_type: str, handler: Callable):
        """Subscribe a handler to an event type."""
        if event_type not in cls._listeners:
            cls._listeners[event_type] = []
        cls._listeners[event_type].append(handler)
        logger.info(f"Subscribed handler {handler.__name__} to {event_type}")

    @classmethod
    def publish(cls, event_type: str, payload: Dict[str, Any]):
        """Publish an event to all subscribers."""
        handlers = cls._listeners.get(event_type, [])
        logger.info(f"Publishing event {event_type} to {len(handlers)} handlers")
        
        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                logger.error(f"Handler {handler.__name__} failed: {str(e)}")

    @classmethod
    def publish_async(cls, event_type: str, payload: Dict[str, Any]):
        """Publish event via Channels (WebSocket/Async)."""
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                "events",
                {"type": "send_event", "event_type": event_type, "payload": payload}
            )

# Global instance
event_bus = EventBus()
