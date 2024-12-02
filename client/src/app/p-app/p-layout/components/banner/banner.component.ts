import { Component, Input } from "@angular/core";

@Component({
  selector : "horizontal-banner",
  template :`
  <div class="wrapper-banner">
    <img [src] = "srcImage" [alt]="altImage" class="bannerImage">
  </div>
  `,
  styleUrls : ["./baner.component.scss"]
})
export class HorizontalBannerComponent{
  @Input() srcImage = "";
  @Input() altImage ="your alt image"

}
