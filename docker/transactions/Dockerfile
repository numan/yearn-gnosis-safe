FROM gnosispm/safe-transaction-service:v3.4.17

COPY run_web.sh /app/run_web.sh

COPY bootstrap/services/retryable_index_service.py /app/safe_transaction_service/history/services/retryable_index_service.py
COPY bootstrap/management/commands/reindex_master_copies_with_retry.py /app/safe_transaction_service/history/management/commands/reindex_master_copies_with_retry.py