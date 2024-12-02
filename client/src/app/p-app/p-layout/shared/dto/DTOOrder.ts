export class DTOOrder {
  ProductID: number;
  OrderID: number;
  UserID: number;
  CutomerName: string;
  Address: string;
  Phone: string;
  PaymentID: number;
  StatusID: number;
  PayIn: string;
  CreateAt: string;
  Amount: number;

  constructor(
    productID: number,
    orderID: number,
    userID: number,
    customerName: string,
    address: string,
    phone: string,
    paymentID: number,
    statusID: number,
    payIn: string,
    createAt: string,
    amount: number
  ) {
    this.ProductID = productID;
    this.OrderID = orderID;
    this.UserID = userID;
    this.CutomerName = customerName;
    this.Address = address;
    this.Phone = phone;
    this.PaymentID = paymentID;
    this.StatusID = statusID;
    this.PayIn = payIn;
    this.CreateAt = createAt;
    this.Amount = amount;
  }
}
