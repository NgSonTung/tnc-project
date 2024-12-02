import { Component, Input, OnInit } from '@angular/core';
import { BreadCrumbItem } from "@progress/kendo-angular-navigation";
import { Ps_UtilObjectService } from 'src/app/p-lib/ultilities/ulity.object';

const defaultItems: BreadCrumbItem[] = [
  {
    text: "",
    title: "",
    icon: "icon_home.svg",
  },
  {
    text: "Trang chủ",
    title: "",
    icon: ""
  }
];
@Component({
  selector: 'app-breadcrumb',
  templateUrl: './breadcrumb.component.html',
  styleUrls: ['./breadcrumb.component.scss']
})
export class BreadcrumbComponent implements OnInit {
  items: BreadCrumbItem[] = [...defaultItems];

  //truyền param từ url của giao diện 
  @Input() plusBreadCrumbText: string[] = [];

  ngOnInit(): void {
    if (Ps_UtilObjectService.hasListValue(this.plusBreadCrumbText)) {
      this.plusBreadCrumbText.forEach(item => {
        this.items.push({ text: item, title: item });
      })
    }
  }
}
