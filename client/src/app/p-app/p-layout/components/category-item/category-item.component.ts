import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-category-item',
  templateUrl: './category-item.component.html',
  styleUrls: ['./category-item.component.scss'],
})
export class CategoryItemComponent {
  @Input() img: string = '';
  @Input() title: string = '';
  @Input() subTitle: string = '';
  @Input() color: string = '';
  constructor(private router: Router) {}
  navigateToUrl() {
    console.log('CCCCCCCC');

    this.router.navigateByUrl('/category/' + this.title);
  }
}
