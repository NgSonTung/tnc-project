module.exports = class DTOOrder {
  constructor(data) {
    this.OrderID = data.OrderID;
    this.UserID = data.UserID;
    this.CustomerName = data.CustomerName;
    this.Address = data.Address;
    this.email = data.email ?? null;
    this.Phone = data.Phone;
    this.PaymentID = data.PaymentID;
    this.StatusID = data.StatusID;
    if (!data.CreatedAt) data.CreatedAt = new Date().toISOString();
    this.CreatedAt = data.CreatedAt;
  }
};
