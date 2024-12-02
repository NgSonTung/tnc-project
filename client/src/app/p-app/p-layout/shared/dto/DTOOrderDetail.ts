export class DTOOrderDetail {
  OrderID: number;
  ProductID: string;
  Amount: number;
  CreateAt: string;

  constructor(
    orderID: number,
    productID: string,
    amount: number,
    createAt: string
  ) {
    this.OrderID = orderID;
    this.ProductID = productID;
    this.Amount = amount;
    this.CreateAt = createAt;
  }
}
