from manim import *
from colour import Color

template = TexTemplate(preamble=r'\usepackage{textcomp}\usepackage{gensymb}')

# sws ... stroke width scale, class overrides scale function to scale 
# stroke width of VMobject with the same scaling factor
class swsCircle(Circle):
    def __init__(self, radius: float | None = None, color: Color | str = WHITE, **kwargs):
        super().__init__(radius, color, **kwargs)

    def scale(self, scale_factor: float, **kwargs):
        self.set_stroke(width=self.get_stroke_width()*scale_factor)
        return super().scale(scale_factor, **kwargs)

class swsLine(Line):
    def __init__(self, start=LEFT, end=RIGHT, buff=0, path_arc=None, **kwargs):
        super().__init__(start, end, buff, path_arc, **kwargs)

    def scale(self, scale_factor: float, **kwargs):
        self.set_stroke(width=self.get_stroke_width()*scale_factor)
        return super().scale(scale_factor, **kwargs)

class swsArc(Arc):
    def __init__(self, radius: float = 1.0, start_angle=0.0, angle=0.0, num_components=9, arc_center=ORIGIN, **kwargs):
        super().__init__(radius, start_angle, angle, num_components, arc_center, **kwargs)

    def scale(self, scale_factor: float, **kwargs):
        self.set_stroke(width=self.get_stroke_width()*scale_factor)
        self.set(radius = self.radius*scale_factor)
        return super().scale(scale_factor, **kwargs)

class CircleWithAngle(VGroup):
    def __init__(
        self,
        ang_end=90*DEGREES,
        ang_start=0*DEGREES,
        radius=3.0,
        small_radius=0.72,
        origin=ORIGIN,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.ang_end = ang_end
        self.ang_start = ang_start
        self.radius = radius
        self.small_radius = small_radius
        self.tex_radius = self.small_radius+3*SMALL_BUFF
        self.origin = origin

        self.vt_1 = ValueTracker()

        self.circle = swsCircle(
            radius = self.radius,
            stroke_width = 0.7,
            color = "#1e1e1e"
        )

        self.base_line = swsLine(
            self.origin,
            self.radius*RIGHT
        )

        self.a_line = swsLine(
            self.origin,
            self.radius*RIGHT
        )
        self.a_line.add_updater(
            lambda m: m.set_angle(self.vt_1.get_value())
        )

        self.ang = swsArc(
            radius = self.small_radius,
            start_angle=self.base_line.get_angle(),
            angle=self.a_line.get_angle(),
            arc_center=self.base_line.get_start(),
            color=YELLOW
        )
        self.ang.add_updater(self.ang_update)

        self.tex = MathTex(r"\theta", color=YELLOW).move_to(RIGHT*20)
        self.tex.add_updater(self.tex_pos_update)

        self.add(
            self.circle,
            self.base_line,
            self.a_line,
            self.ang,
            self.tex
        )
    
    def ang_update(self,m):
        m.become(
            swsArc(
                radius = self.small_radius,
                start_angle=self.base_line.get_angle(),
                angle=self.vt_1.get_value(),
                arc_center=self.base_line.get_start(),
                color=YELLOW
            )
        )

    def tex_pos_update(self,m):
        if self.vt_1.get_value() > 28*DEGREES:
            m.move_to(
                Arc(
                    radius=self.tex_radius,
                    start_angle=self.base_line.get_angle(),
                    angle=self.vt_1.get_value(),
                    arc_center=self.base_line.get_start()
                ).point_from_proportion(0.5)
            )

    def scale(self, scale_factor: float, **kwargs):
        circle_center = self.circle.get_center()
        self.circle.scale(scale_factor, about_point=circle_center)
        self.base_line.scale(scale_factor, about_point=circle_center)
        self.a_line.scale(scale_factor, about_point=circle_center)
        self.ang.scale(scale_factor, about_point=circle_center)
        self.small_radius = self.small_radius*scale_factor
        self.tex_radius = self.small_radius+3*SMALL_BUFF*scale_factor
        self.tex.scale(scale_factor, about_point=circle_center).move_to(
            Arc(
                radius=self.tex_radius,
                start_angle=self.base_line.get_angle(),
                angle=self.vt_1.get_value(),
                arc_center=self.base_line.get_start()
            ).point_from_proportion(0.5)
        )
        return self

class CreateAngles(Scene):
    # ang_values = np.random.uniform(28.0, 360.0, 6)
    ang_values = [163.0, 32.0, 227.0, 90.0, 270.0, 336.0]
    itm = ["a)", "b)", "c)", "d)", "e)", "f)"]

    def construct(self):
        scale_fct = 0.4
        cwa = [CircleWithAngle() for x in range(6)]
        tps = self.get_target_points(scale_fct, cwa[0])
        d = [Dot().shift(tps[i]) for i in range(6)]

        for i in range(6):
            cwa[i].shift(3*RIGHT)
            vt = cwa[i].vt_1
            ang_tex = Tex(
                r"$\theta="+
                str(int(vt.get_value()/DEGREES))+
                r"\degree$",
                tex_template=template
            )
            ang_tex.next_to(
                cwa[i], 
                buff=0.0, 
                index_of_submobject_to_align=0,
                aligned_edge=UP)
            ang_tex.shift(9*SMALL_BUFF*LEFT)

            ang_tex.add_updater(
                lambda m: m.become(
                    Tex(
                        r"$\theta="+
                        str(int(vt.get_value()/DEGREES))+
                        r"\degree$",
                        tex_template=template
                    ).next_to(
                        cwa[i], 
                        buff=0.0, 
                        index_of_submobject_to_align=0,
                        aligned_edge=UP
                    ).shift(9*SMALL_BUFF*LEFT)
                )
            )

            self.play(Create(cwa[i]), run_time=2)
            self.add(ang_tex)
            self.play(
                vt.animate.set_value(self.ang_values[i]*DEGREES),
                run_time=4/360*self.ang_values[i],
                rate_func=linear
            )
            self.wait(1.5)
            self.remove(ang_tex)
            self.play(cwa[i].animate.scale(scale_fct))
            self.play(cwa[i].animate.move_to(d[i]))

            item_tex = Tex(r"\item["+self.itm[i]+"]", font_size=27)
            item_tex.next_to(
                cwa[i],
                buff=0.0,
                direction=LEFT,
                index_of_submobject_to_align=0,
                aligned_edge=UL
            )
            self.add(item_tex)
            self.wait()

        tex_group = self.get_tex_angles()
        which_kind_tex = VGroup(*tex_group)
        which_kind_tex.arrange_in_grid(
            cols=1, 
            cell_alignment=LEFT,
            buff=MED_LARGE_BUFF,
        )
        which_kind_tex.next_to(
            cwa[4],
            direction=RIGHT+UP, 
            buff=LARGE_BUFF,
            index_of_submobject_to_align=0,
        )
        self.play(Write(which_kind_tex))
        self.wait()

    def get_tex_angles(self) -> list[Tex]:
        tex_group = []
        for i in range(6):
            tex_desc = Tex(
                self.itm[i]+\
                " "+\
                self.get_ang_kind(self.ang_values[i])+\
                r" Winkel ($"+\
                str(int(self.ang_values[i]))+\
                r"\degree$)",
                tex_template=template
            )
            tex_desc[1].set_fill(color=YELLOW)
            tex_group.append(tex_desc)

        return tex_group

    def get_ang_kind(self, ang: float) -> str:
        str_a = r"{{\textbf{\textit{"
        if ang > 0 and ang < 90:
            return str_a + r"spitzer}}}}"
        elif ang == 90:
            return str_a + r"rechter}}}}"
        elif ang > 90 and ang < 180:
            return str_a + r"stumpfer}}}}"
        elif ang == 180:
            return str_a + r"gestreckter}}}}"
        elif ang > 180 and ang < 360:
            return str_a + r"erhabener}}}}"
        elif ang == 360:
            return str_a + r"voller}}}}"
        elif ang == 0:
            return str_a + r"Null}}}}"
        else:
            return str_a + r"unbestimmter}}}}"

    def get_target_points(
        self, 
        scale_fct: float,
        cwa: CircleWithAngle 
    ) -> list:

        cd = cwa.circle.height*scale_fct
        fh = config.frame_height
        fw = config.frame_width
        buf = (fh-3*cd)/4
        x_0 = -fw/2.0+(buf+cd/2.0)
        y_0 = fh/2.0-(buf+cd/2.0)
        incr = cd+buf
        points = []
        for i in range(2):
            for j in range(3):
                points.append(
                    np.array(
                        [
                            x_0+(i*incr),
                            y_0-(j*incr),
                            0.0
                        ],
                        dtype=float
                    )
                )

        return points

SCENE_TO_RENDER = CreateAngles