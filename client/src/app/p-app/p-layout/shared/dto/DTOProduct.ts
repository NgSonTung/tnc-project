export class DTOProduct {
  ProductID: number;
  Stock: number;
  Name: string;
  Favorite: number;
  CategoryID: number;
  Price: number;
  BrandID: number;
  Image: string;
  Sale: number;
  Description: string;
  StatusID: number;
  createdAt: string;
  Base64Image?: string;

  constructor() {
    this.ProductID = 0;
    this.Stock = 0;
    this.Name = '';
    this.Favorite = null;
    this.CategoryID = null;
    this.Price = null;
    this.BrandID = null;
    this.Image = null;
    this.Sale = null;
    this.Description = '';
    this.StatusID = null;
    this.createdAt = '';
  }
}
