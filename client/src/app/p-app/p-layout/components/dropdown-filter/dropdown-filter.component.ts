import {
  Component,
  ElementRef,
  EventEmitter,
  Input,
  Output,
  ViewChild,
} from '@angular/core';
import { Subject, takeUntil } from 'rxjs';
import { ProductAPIService } from 'src/app/p-app/product/shared/services/product-api.service';

@Component({
  selector: 'dropdown-filter',
  templateUrl: './dropdown-filter.component.html',
  styleUrls: ['./dropdown-filter.component.scss'],
})
export class dropdownFilterComponent {
  @ViewChild('myDropdownList') myDropdownList: ElementRef;

  queryFilter: string[] = [];
  active: boolean = false;
  query: string = '';
  labelFilter: any[] = [];
  filterPriceStart: number;
  filterPriceEnd: number;

  //Subscription
  ngUnsubscribe = new Subject<void>();

  @Input() filterbyPrice: boolean = false;
  @Input() activeSearch: boolean = false;
  @Input() titleFilter: string = 'default';
  @Input() placeholderSearch: string = `Tìm ${this.titleFilter}`;
  @Input() data: any = [];
  checkedItems: string[] = [];

  @Output() filterURL = new EventEmitter<string>();
  @Output() filterPrice = new EventEmitter<any[]>();
  constructor(private productService: ProductAPIService) {}

  ngOnInit(): void {
    if (this.filterbyPrice) {
      this.titleFilter = 'Mức giá';
    }
    console.log(this.data);
    this.productService
      .getArrlabelFilter()
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe((res) => {
        this.labelFilter = [...res];
      });
    this.productService
      .getRemoveItem()
      .pipe(takeUntil(this.ngUnsubscribe))
      .subscribe((res) => {
        if (res.length > 0) {
          const arrQuery = this.query.split(',').filter(Boolean);
          console.log('resRM', res);
          console.log('arrQuery', arrQuery);
          this.query = arrQuery.filter((i) => !i.includes(`:${res}`)).join(',');
          console.log(this.query);
          this.checkedItems = this.checkedItems.filter((i) => i != res[0]);
        }
      });
  }

  clickBoxFilter() {
    const element = this.myDropdownList.nativeElement;
    const hasClass = element.classList.contains('active-dropdown-list');
    hasClass ? (this.active = false) : (this.active = true);
  }

  handleCheck(event: any, item: any) {
    console.log(event.target.id);
    var ischecked = event.target.checked;
    // event.target.checked
    //   ? (this.query += `${event.target.name}:${event.target.value},`)
    //   : (this.query = this.query.replace(
    //       `${event.target.name}:${event.target.value}`,
    //       ''
    //     ));

    // this.filterURL.emit(this.query);
    ischecked
      ? this.productService.setQueryFilter(
          `${event.target.name}:${event.target.value},`
        )
      : this.productService.setRemoveItem([event.target.value]);
    console.log('this.query dropdown', this.query);

    var lbName = item.labelName;
    if (ischecked) {
      this.checkedItems.push(lbName);
      this.labelFilter.push({
        title: this.titleFilter,
        labelName: lbName,
      });
      this.productService.setArrlabelFilter(this.labelFilter);
    } else {
      this.checkedItems = this.checkedItems.filter((item) => item !== lbName);
      this.labelFilter = this.labelFilter.filter((i) => i.labelName != lbName);
      this.productService.setArrlabelFilter(this.labelFilter);
    }
  }
  handleFilterPrice() {
    console.log([this.filterPriceStart, this.filterPriceEnd]);
    this.filterPrice.emit([this.filterPriceStart, this.filterPriceEnd]);
  }
}
