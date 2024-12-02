export class DTOCategory {
  CategoryID: number;
  CategoryName: string;
  CreateAt: string;

  constructor(categoryID: number, categoryName: string, createAt: string) {
    this.CategoryID = categoryID;
    this.CategoryName = categoryName;
    this.CreateAt = createAt;
  }
}
