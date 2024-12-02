import { Component, EventEmitter, Input,Output } from "@angular/core";

@Component({
  selector :"nav-title",
  template :`
  <div class="wrapper-title">
  <span class="title">{{ inputTitle }}</span>
</div>
`,
  styleUrls :["./title.component.scss"]
})
export class TitleComponent {

  @Input() inputTitle = "your title"

}
