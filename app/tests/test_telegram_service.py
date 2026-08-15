import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.telegram_service import TelegramService


@pytest.mark.asyncio
async def test_send_message_success():
    service = TelegramService()

    mock_response = MagicMock()
    mock_response.json.return_value = {"ok": True}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await service.send_message("hello")

    assert result == {"ok": True}
    mock_client.post.assert_awaited_once()
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_raises_exception():
    service = TelegramService()

    error = httpx.HTTPStatusError(
        "Bad request",
        request=MagicMock(),
        response=MagicMock(status_code=400),
    )

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=error)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with pytest.raises(httpx.HTTPStatusError):
            await service.send_message("hello")
