import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';

import { RESOURCES } from '../../core/data/resources.data';
import { HeroVideoComponent } from '../../shared/components/hero-video/hero-video.component';



@Component({

  selector: 'app-resources',

  standalone: true,

  imports: [HeroVideoComponent, RouterLink],

  templateUrl:

    './resources.component.html',

  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrl:

    './resources.component.css'

})
export class ResourcesComponent {


resources =
RESOURCES;


}