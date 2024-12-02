module.exports = class DTOOrderDetails {
  constructor(data) {
    this.OrderID = data.OrderID;
    this.ProductID = data.ProductID ?? null;
    this.Amount = data.Amount ?? null;
    if (!data.CreatedAt) data.CreatedAt = new Date().toISOString();
    this.CreatedAt = data.CreatedAt;
  }
};
