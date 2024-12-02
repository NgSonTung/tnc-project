import {
  Component,
  Input,
  OnInit,
  Output,
  EventEmitter,
  SkipSelf,
} from '@angular/core';
import { DataService } from '../shared/service/data.service';
import {
  Observable,
  Subject,
  Subscription,
  concatMap,
  of,
  takeUntil,
} from 'rxjs';
import { ProductService } from 'src/app/p-app/p-layout/shared/services/product.service';
import { DTOProduct } from 'src/app/p-app/p-layout/shared/dto/DTOProduct';
import { PageChangeEvent } from '@progress/kendo-angular-grid';
import { FormControl, FormGroup } from '@angular/forms';
import { NotificationPopupService } from 'src/app/p-app/p-layout/shared/services/notification.service';
import { CategoryService } from 'src/app/p-app/p-layout/shared/services/category.service';
import { BrandService } from 'src/app/p-app/p-layout/shared/services/brand.service';
import { DTOCategory } from 'src/app/p-app/p-layout/shared/dto/DTOCategory';
import { DTOBrand } from 'src/app/p-app/p-layout/shared/dto/DTOBrand';

class ImageSnippet {
  constructor(public src: string, public file: File) {}
}

@Component({
  selector: 'app-main-table',
  templateUrl: './main-table.component.html',
  styleUrls: ['./main-table.component.scss'],
})
export class MainTableComponent implements OnInit {
  #subscription: Subscription = new Subscription();
  productList: Subject<any> = new Subject<any>();
  ngUnsubscription$ = new Subject<void>();
  page: number = 1;
  pageSize: number = 20;
  skip: number = 0;
  selectedProduct: DTOProduct;
  isSelectedProduct: boolean = false;
  isDeletePopupOpened: boolean = false;
  isCreatePopupOpened: boolean = false;
  listCategory = new Subject<any>();
  listBrand = new Subject<any>();
  imgBaseName: any;

  productForm: FormGroup = new FormGroup({
    Name: new FormControl(''),
    Stock: new FormControl(),
    Description: new FormControl(''),
    Price: new FormControl(),
    Favorite: new FormControl(0),
    CategoryID: new FormControl(),
    BrandID: new FormControl(),
    Image: new FormControl(''),
    Sale: new FormControl<number>(0),
  });

  constructor(
    @SkipSelf() private dataService: DataService,
    private productService: ProductService,
    private notiService: NotificationPopupService,
    private cateService: CategoryService,
    private brandService: BrandService
  ) {}

  ngOnInit(): void {
    this.fetchData();
  }

  tableName: string = 'Table name';
  checkedList: number[] = [];
  totalPages: number = 0;
  data: any = [];
  @Output() toggleSubTable: EventEmitter<void> = new EventEmitter<void>();
  loading: boolean = false;

  fetchData() {
    this.loading = true;
    this.productService
      .getListProduct(this.page, this.pageSize)
      .pipe(takeUntil(this.ngUnsubscription$))
      .subscribe((res) => {
        console.log(res.Data);
        this.productList.next({
          data: res.Data,
          total: res.TotalProduct,
        });
        this.loading = false;
      });
  }

  updateProductHandle() {
    const updatedInfo = this.productForm.value;
    this.productService
      .updateData(this.selectedProduct.ProductID, updatedInfo)
      .pipe(takeUntil(this.ngUnsubscription$))
      .subscribe((res) => {
        if (res.Code === 200) {
          this.notiService.onSuccess('Cập nhật sản phẩm thành công');
          this.fetchData();
        } else {
          this.notiService.onError('Cập nhật sản phẩm thất bại');
          console.log('error');
        }
      });
  }

  deleteProduct() {
    this.productService
      .deleteDataById(this.selectedProduct.ProductID)
      .pipe(takeUntil(this.ngUnsubscription$))
      .subscribe((res) => {
        if (res.Code === 200) {
          this.notiService.onSuccess('Xóa sản phẩm thành công');
          this.fetchData();
        } else {
          this.notiService.onError('Xóa sản phẩm thất bại');
          console.log('error');
        }
        this.isDeletePopupOpened = false;
        this.isSelectedProduct = false;
      });
  }

  openCreateForm() {
    this.productForm.reset();
    this.isCreatePopupOpened = true;
    this.getBrands();
    this.getCategories();
  }

  createProduct() {
    const createdInfo = this.productForm.value;
    createdInfo.Favorite = 0;
    createdInfo.Image = '';

    this.productService
      .createData(createdInfo)
      .pipe(
        concatMap((res) => {
          if (res.Code === 200) {
            const productID = res.Data.ProductID;
            return this.productService.addImageProduct(
              this.imgBaseName,
              productID
            );
          } else {
            this.notiService.onError('Đã xảy ra lỗi');
            return of();
          }
        }),
        takeUntil(this.ngUnsubscription$)
      )
      .subscribe((res) => {
        if (res.Code === 200) {
          this.notiService.onSuccess('Thêm mới sản phẩm thành công');
          this.productForm.reset();
          this.fetchData();
        } else {
          this.notiService.onError('Thêm mới sản phẩm thất bại');
          console.log('error');
        }
        this.isCreatePopupOpened = false;
      });
  }

  uploadFile(inputImg: any) {
    const file: File = inputImg.files[0];
    const reader = new FileReader();

    reader.addEventListener('load', (event: any) => {
      this.imgBaseName = file;
    });

    reader.readAsDataURL(file);
  }

  updateImg(inputImg: any) {
    console.log('this.selectedProduct vvvvvvvvvvvv', this.selectedProduct);

    const file: File = inputImg.files[0];
    const reader = new FileReader();

    reader.addEventListener('load', (event: any) => {
      this.imgBaseName = file;
      console.log(this.imgBaseName);

      this.productService
        .addImageProduct(this.imgBaseName, this.selectedProduct.ProductID)
        .pipe(takeUntil(this.ngUnsubscription$))
        .subscribe((res) => {
          if (res.Code === 200) {
            this.notiService.onSuccess('Cập nhật ảnh sản phẩm thành công');
            this.fetchData();
          } else {
            this.notiService.onError('Cập nhật ảnh sản phẩm thất bại');
          }
          this.imgBaseName = null;
        });
    });

    reader.readAsDataURL(file);
  }

  convertToBase64(file: File): void {
    const reader = new FileReader();

    reader.onload = (event: any) => {
      const string = event.target.result;
      const base64String = string.split(',')[1];
      console.log(base64String); // Here's your base64 encoded image
    };

    reader.readAsDataURL(file);
  }

  getCategories() {
    this.cateService
      .getListCategory()
      .pipe(takeUntil(this.ngUnsubscription$))
      .subscribe((res) => {
        if (res.Code === 200) {
          this.listCategory.next(res.Data);
        }
      });
  }

  getBrands() {
    this.brandService
      .getListBrand()
      .pipe(takeUntil(this.ngUnsubscription$))
      .subscribe((res) => {
        if (res.Code === 200) {
          this.listBrand.next(res.Data);
        }
      });
  }

  public pageChange(state: PageChangeEvent): void {
    console.log(state);
    this.page = state.skip / this.pageSize + 1;
    this.skip = state.skip;
    this.fetchData();
  }

  selectProduct(data: any) {
    this.selectedProduct = data;
    this.selectedProduct.Sale = data.Sale * 1;
    this.productForm.patchValue(data);
    console.log(this.productForm.value);

    this.isSelectedProduct = true;
  }

  getObjectKeys(obj: any): string[] {
    return Object.keys(obj[0]);
  }

  getObjectValues(obj: any): string[] {
    return Object.values(obj);
  }

  onToggleSubTable() {
    this.toggleSubTable.emit();
  }

  formatPhoneNumber(phoneNumber: string): string {
    return phoneNumber.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
  }

  handleCheckAll(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.checkedList = target.checked
      ? this.data.map((item: any) => item.id)
      : (this.checkedList = []);
  }

  toggleCheckbox(id: number): void {
    if (this.checkedList.includes(id)) {
      this.checkedList = this.checkedList.filter((itemId) => itemId !== id);
    } else {
      this.checkedList.push(id);
    }
  }

  getPagination(): string[] {
    if (this.totalPages > 0) {
      const pagination: string[] = [];
      const totalPages = this.totalPages;
      const currentPage = this.page;

      const maxVisiblePages = 6;

      pagination.push('1');

      if (currentPage <= 3) {
        for (let i = 2; i <= Math.min(maxVisiblePages - 2, totalPages); i++) {
          pagination.push(i.toString());
        }
        if (totalPages > maxVisiblePages) {
          pagination.push('...', totalPages.toString());
        }
      } else if (currentPage >= totalPages - 3) {
        if (totalPages > maxVisiblePages) {
          pagination.push('...', (totalPages - maxVisiblePages + 3).toString());
        }
        for (let i = totalPages - 2; i <= totalPages; i++) {
          pagination.push(i.toString());
        }
      } else {
        pagination.push(
          '...',
          (currentPage - 1).toString(),
          currentPage.toString(),
          (currentPage + 1).toString(),
          '...'
        );
      }
      if (!pagination.includes(this.totalPages.toString()) && totalPages > 1) {
        pagination.push(this.totalPages.toString());
      }

      return pagination;
    } else return [''];
  }

  getHeight(items: number): string {
    return ((this.pageSize - items) * 100) / this.pageSize + '%';
  }

  setPage(value: any) {
    const newPage = parseInt(value);
    if (!isNaN(newPage)) {
      this.page =
        newPage * this.pageSize - this.data.length > this.pageSize ||
        newPage <= 0
          ? this.page
          : newPage;
    }
    this.fetchData();
  }

  ngOnDestroy(): void {
    this.#subscription.unsubscribe();
  }
}
