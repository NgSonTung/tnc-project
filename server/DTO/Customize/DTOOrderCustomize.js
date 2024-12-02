const DTOOrder = require("../Default/DTOOrder");

module.exports = class DTOOrderCustomize extends DTOOrder {
  constructor(data) {
    super(data);
    this.StatusName = data.StatusName;
    this.PaymentName = data.PaymentName;
    this.TotalAmount = data.TotalAmount;
    this.TotalPrice = data.TotalPrice;
  }
};
