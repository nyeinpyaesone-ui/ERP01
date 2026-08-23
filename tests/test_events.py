"""
Tests for Real-Time Event Bus and Handlers
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase

from src.core.events import EventBus, event_bus
from src.core.handlers import (
    handle_stock_adjusted,
    handle_low_stock_alert,
    handle_order_created,
    handle_order_confirmed,
    handle_order_shipped,
    register_handlers
)


class TestEventBus(TestCase):
    """Test EventBus functionality."""

    def setUp(self):
        # Reset listeners for each test
        EventBus._listeners = {}

    def test_event_bus_singleton(self):
        """Test that EventBus is a singleton."""
        bus1 = EventBus()
        bus2 = EventBus()
        self.assertIs(bus1, bus2)

    def test_subscribe_and_publish(self):
        """Test subscribing and publishing events."""
        handler = Mock()
        
        event_bus.subscribe('test_event', handler)
        payload = {'key': 'value'}
        event_bus.publish('test_event', payload)
        
        handler.assert_called_once_with(payload)

    def test_publish_to_multiple_handlers(self):
        """Test publishing to multiple subscribers."""
        handler1 = Mock()
        handler2 = Mock()
        
        event_bus.subscribe('multi_event', handler1)
        event_bus.subscribe('multi_event', handler2)
        
        payload = {'data': 'test'}
        event_bus.publish('multi_event', payload)
        
        handler1.assert_called_once_with(payload)
        handler2.assert_called_once_with(payload)

    def test_handler_exception_does_not_stop_others(self):
        """Test that one handler's exception doesn't stop others."""
        handler1 = Mock(side_effect=Exception("Error in handler 1"))
        handler2 = Mock()
        
        event_bus.subscribe('error_event', handler1)
        event_bus.subscribe('error_event', handler2)
        
        payload = {'data': 'test'}
        event_bus.publish('error_event', payload)
        
        handler1.assert_called_once()
        handler2.assert_called_once_with(payload)

    def test_publish_non_existent_event(self):
        """Test publishing to an event with no subscribers."""
        # Should not raise any error
        event_bus.publish('non_existent', {'data': 'test'})


class TestEventHandlers(TestCase):
    """Test event handler functions."""

    @patch('src.core.handlers.logger')
    def test_handle_stock_adjusted(self, mock_logger):
        """Test stock adjusted handler."""
        payload = {
            'sku': 'PROD-001',
            'old_quantity': 100,
            'new_quantity': 90,
            'change': -10
        }
        
        handle_stock_adjusted(payload)
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        self.assertIn('PROD-001', call_args)
        self.assertIn('100 -> 90', call_args)

    @patch('src.core.handlers.logger')
    def test_handle_low_stock_alert(self, mock_logger):
        """Test low stock alert handler."""
        payload = {
            'sku': 'PROD-002',
            'current_quantity': 5,
            'reorder_point': 10
        }
        
        handle_low_stock_alert(payload)
        
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]
        self.assertIn('LOW STOCK ALERT', call_args)
        self.assertIn('PROD-002', call_args)

    @patch('src.core.handlers.logger')
    def test_handle_order_created(self, mock_logger):
        """Test order created handler."""
        payload = {
            'order_reference': 'ORD-12345',
            'customer_id': 1,
            'total_amount': '99.99',
            'items_count': 3
        }
        
        handle_order_created(payload)
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        self.assertIn('NEW ORDER', call_args)
        self.assertIn('ORD-12345', call_args)

    @patch('src.core.handlers.logger')
    def test_handle_order_confirmed(self, mock_logger):
        """Test order confirmed handler."""
        payload = {
            'order_reference': 'ORD-12345',
            'confirmed_at': '2024-01-01T10:00:00Z'
        }
        
        handle_order_confirmed(payload)
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        self.assertIn('ORDER CONFIRMED', call_args)

    @patch('src.core.handlers.logger')
    def test_handle_order_shipped(self, mock_logger):
        """Test order shipped handler."""
        payload = {
            'order_reference': 'ORD-12345',
            'shipped_at': '2024-01-02T14:00:00Z'
        }
        
        handle_order_shipped(payload)
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        self.assertIn('ORDER SHIPPED', call_args)

    @patch('src.core.handlers.event_bus')
    def test_register_handlers(self, mock_event_bus):
        """Test handler registration."""
        register_handlers()
        
        # Check all handlers are subscribed
        expected_events = [
            'stock_adjusted',
            'low_stock_alert',
            'order_created',
            'order_confirmed',
            'order_shipped'
        ]
        
        for event in expected_events:
            mock_event_bus.subscribe.assert_any_call(event, pytest.ANY)
