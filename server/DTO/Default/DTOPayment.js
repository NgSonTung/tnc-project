module.exports = class DTOPayment {
  constructor(data) {
    this.PaymentID = data.PaymentID;
    this.PaymentName = data.PaymentName;
    this.PaymentType = data.PaymentType ?? null;
    if (!data.CreatedAt) data.CreatedAt = new Date().toISOString();
    this.CreatedAt = data.CreatedAt;
  }
};
