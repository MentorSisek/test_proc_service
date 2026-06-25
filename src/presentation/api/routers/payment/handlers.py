from fastapi import APIRouter, Depends, status

from presentation.api.dependency import (
	CreatePaymentUseCaseDep,
	GetPaymentUseCaseDep,
	IdempotencyKeyDep,
	verify_api_key,
)

from .schemas import CreatePaymentRequest, CreatePaymentResponse, PaymentResponse

router = APIRouter(
	prefix='/api/v1/payments',
	tags=['Payment'],
	dependencies=[Depends(verify_api_key)],
)


@router.post(
	'',
	response_model=CreatePaymentResponse,
	status_code=status.HTTP_202_ACCEPTED,
)
async def create_payment(
	request: CreatePaymentRequest,
	idempotency_key: IdempotencyKeyDep,
	use_case: CreatePaymentUseCaseDep,
):
	"""Создать платёж.

	Платёж сохраняется в статусе `pending`, событие кладётся в outbox и асинхронно
	публикуется в очередь `payments.new`. Повторный запрос с тем же `Idempotency-Key`
	возвращает ранее созданный платёж.
	"""
	payment = await use_case.execute(
		idempotency_key=idempotency_key,
		amount=request.amount,
		currency=request.currency,
		description=request.description,
		metadata=request.metadata,
		webhook_url=str(request.webhook_url) if request.webhook_url else None,
	)
	return CreatePaymentResponse.create(payment)


@router.get(
	'/{payment_id}',
	response_model=PaymentResponse,
	status_code=status.HTTP_200_OK,
)
async def get_payment(
	payment_id: str,
	use_case: GetPaymentUseCaseDep,
):
	"""Получить детальную информацию о платеже."""
	payment = await use_case.execute(payment_id=payment_id)
	return PaymentResponse.create(payment)
