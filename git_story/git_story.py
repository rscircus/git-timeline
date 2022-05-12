from manim import *
import git

class GitStory(MovingCameraScene):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.drawnCommits = {}

    def construct(self):
        self.repo = git.Repo(search_parent_directories=True)

        commit = self.repo.commit(self.args.last_commit)
        self.earliestCommitId = None
        if ( self.args.earliest_commit ):
            self.earliestCommitId = self.repo.commit(self.args.earliest_commit).hexsha

        if ( not self.args.reverse ):
            commits.reverse()

        logo = ImageMobject(self.args.logo)
        logo.width = 3

        if ( not self.args.no_intro ):
            self.add(logo)

            initialCommitText = Text(self.args.title, font="Monospace", font_size=36).to_edge(UP, buff=1)
            self.add(initialCommitText)
            self.wait(2)
            self.play(FadeOut(initialCommitText))
            self.play(logo.animate.scale(0.25).to_edge(UP, buff=0).to_edge(RIGHT, buff=0))
    
            self.camera.frame.save_state()
            self.play(FadeOut(logo))

        else:
            logo.scale(0.25).to_edge(UP, buff=0).to_edge(RIGHT, buff=0)
            self.camera.frame.save_state()

        i = 0
        prevCircle = None
        toFadeOut = Group()
        self.parseCommits(commit, i, prevCircle, toFadeOut, False)

        self.play(self.camera.frame.animate.move_to(toFadeOut.get_center()))

        self.wait(3)

        self.play(FadeOut(toFadeOut))

        if ( not self.args.no_outro ):

            self.play(Restore(self.camera.frame))

            self.play(logo.animate.scale(4).set_x(0).set_y(0))

            outroTopText = Text(self.args.outro_top_text, font="Monospace", font_size=36).to_edge(UP, buff=1)
            self.play(AddTextLetterByLetter(outroTopText))

            outroBottomText = Text(self.args.outro_bottom_text, font="Monospace", font_size=36).to_edge(DOWN, buff=1)
            self.play(AddTextLetterByLetter(outroBottomText))

            self.wait(3)

    def parseCommits(self, commit, i, prevCircle, toFadeOut, offset):
        if ( i < self.args.commits and commit.hexsha != self.earliestCommitId ):

            if ( len(commit.parents) <= 1 ):
                commitFill = RED
            else:
                commitFill = GRAY

            circle = Circle(stroke_color=commitFill, fill_color=commitFill, fill_opacity=0.25)
            circle.height = 1

            if prevCircle:
                circle.next_to(prevCircle, RIGHT, buff=1.5)

            if ( offset ):
                circle.to_edge(DOWN, buff=-1)
                self.play(self.camera.frame.animate.scale(1.5))

            self.play(self.camera.frame.animate.move_to(circle.get_center()))

            isNewCommit = commit.hexsha not in self.drawnCommits

            if ( not self.args.reverse and not offset and isNewCommit ):
                arrow = Arrow(start=RIGHT, end=LEFT).next_to(circle, LEFT, buff=0)
            elif ( self.args.reverse and offset and isNewCommit ):
                arrow = Arrow(start=prevCircle.get_center(), end=circle.get_center())
            elif ( self.args.reverse and not offset and not isNewCommit ):
                arrow = Arrow(start=prevCircle.get_center(), end=self.drawnCommits[commit.hexsha].get_center())
            else:
                arrow = Arrow(start=LEFT, end=RIGHT).next_to(circle, LEFT, buff=0)

            arrow.width = 1

            commitId = Text(commit.hexsha[0:6], font="Monospace", font_size=20).next_to(circle, UP)

            message = Text('\n'.join(commit.message[j:j+20] for j in range(0, len(commit.message), 20))[:100], font="Monospace", font_size=14).next_to(circle, DOWN)

            if ( isNewCommit ):
                self.play(Create(circle), AddTextLetterByLetter(commitId), AddTextLetterByLetter(message))
                self.drawnCommits[commit.hexsha] = circle

                prevRef = commitId
                if ( commit.hexsha == self.repo.head.commit.hexsha ):
                    head = Rectangle(color=BLUE, fill_color=BLUE, fill_opacity=0.25)
                    head.width = 1
                    head.height = 0.4
                    head.next_to(commitId, UP)
                    headText = Text("HEAD", font="Monospace", font_size=20).move_to(head.get_center())
                    self.play(Create(head), Create(headText))
                    toFadeOut.add(head, headText)
                    prevRef = head

                x = 0
                for branch in self.repo.heads:
                    if ( commit.hexsha == branch.commit.hexsha ):
                        branchText = Text(branch.name, font="Monospace", font_size=20)
                        branchRec = Rectangle(color=GREEN, fill_color=GREEN, fill_opacity=0.25, height=0.4, width=branchText.width+0.25)

                        branchRec.next_to(prevRef, UP)
                        branchText.move_to(branchRec.get_center())

                        prevRef = branchRec 

                        self.play(Create(branchRec), Create(branchText))
                        toFadeOut.add(branchRec, branchText)

                        x += 1
                        if ( x >= self.args.max_branches_per_commit ):
                            break

                x = 0
                for tag in self.repo.tags:
                    if ( commit.hexsha == tag.commit.hexsha ):
                        tagText = Text(tag.name, font="Monospace", font_size=20)
                        tagRec = Rectangle(color=YELLOW, fill_color=YELLOW, fill_opacity=0.25, height=0.4, width=tagText.width+0.25)

                        tagRec.next_to(prevRef, UP)
                        tagText.move_to(tagRec.get_center())

                        prevRef = tagRec

                        self.play(Create(tagRec), Create(tagText))
                        toFadeOut.add(tagRec, tagText)

                        x += 1
                        if ( x >= self.args.max_tags_per_commit ):
                            break

            else:
                self.play(Create(arrow))
                toFadeOut.add(arrow)
                return


            if ( prevCircle ):
                self.play(Create(arrow))
                toFadeOut.add(arrow)

            prevCircle = circle

            toFadeOut.add(circle, commitId, message)

            if ( len(commit.parents) > 0 ):
                if ( self.args.hide_merged_chains):
                    self.parseCommits(commit.parents[0], i+1, prevCircle, toFadeOut, False)
                else:
                    for p in range(len(commit.parents)):
                        self.parseCommits(commit.parents[p], i+1, prevCircle, toFadeOut, False if ( p == 0 ) else True)

        else:
            return
