import { Component, ChangeDetectionStrategy } from '@angular/core';
import { HeroVideoComponent } from '../../shared/components/hero-video/hero-video.component';

@Component({
  selector: 'app-terms',
  imports: [HeroVideoComponent],
  templateUrl: './terms.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrl: './terms.component.css'
})
export class TermsComponent {

}
