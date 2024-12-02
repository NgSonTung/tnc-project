export class DTOPayment {
  PaymentID: number;
  PaymentName: string;
  PaymentType: string;
  CreateAt: string;

  constructor(
    paymentID: number,
    paymentName: string,
    paymentType: string,
    createAt: string
  ) {
    this.PaymentID = paymentID;
    this.PaymentName = paymentName;
    this.PaymentType = paymentType;
    this.CreateAt = createAt;
  }
}
