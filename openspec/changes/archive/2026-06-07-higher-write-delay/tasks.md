## 1. Differentiated proactive delay in api.py

- [x] 1.1 `_REQUEST_DELAY` renamed to `_READ_DELAY = 0.2` and `_WRITE_DELAY = 1.0` constant added
- [x] 1.2 `_proactive_delay` accepts `is_write: bool` and sleeps `_WRITE_DELAY` when True, `_READ_DELAY` when False
- [x] 1.3 `api_request` passes `is_write=body is not None` to `_proactive_delay`

## 2. Test infrastructure updated

- [x] 2.1 `_no_proactive_delay` fixture in conftest.py updated to `lambda is_write=False: None`

## 3. Proactive delay behaviour tested

- [x] 3.1 GET call causes `time.sleep` to be called with `0.2`
- [x] 3.2 POST call causes `time.sleep` to be called with `1.0`
- [x] 3.3 GET call does not sleep for `1.0`
