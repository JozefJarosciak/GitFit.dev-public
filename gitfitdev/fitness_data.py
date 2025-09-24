"""
Comprehensive fitness data for GitFit.dev
100 unique entries per category with muscle group tracking
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class Position(Enum):
    STANDING = "standing"
    SITTING = "sitting"
    LYING = "lying"  # lying down or ground exercises

class MuscleGroup(Enum):
    NECK = "neck"
    SHOULDERS = "shoulders"
    CHEST = "chest"
    UPPER_BACK = "upper_back"
    LOWER_BACK = "lower_back"
    ARMS = "arms"
    CORE = "core"
    HIPS = "hips"
    GLUTES = "glutes"
    QUADS = "quads"
    HAMSTRINGS = "hamstrings"
    CALVES = "calves"
    WRISTS = "wrists"
    ANKLES = "ankles"
    FULL_BODY = "full_body"

@dataclass
class Exercise:
    description: str
    muscle_groups: List[MuscleGroup]
    difficulty: int  # 1-3 (easy, medium, hard)
    position: Position

@dataclass
class Stretch:
    description: str
    muscle_groups: List[MuscleGroup]
    hold_time: int  # seconds
    position: Position

# 100 Unique Stretches with muscle groups (all time-based)
STRETCHES = [
    # Neck stretches (1-10)
    Stretch("Slowly tilt your head sideways toward your right shoulder, then left", [MuscleGroup.NECK], 30, Position.SITTING),
    Stretch("Lower your chin down to touch your chest", [MuscleGroup.NECK], 30, Position.SITTING),
    Stretch("Tilt your head back to look up at the ceiling", [MuscleGroup.NECK], 30, Position.SITTING),
    Stretch("Turn your head to look over your right shoulder, then left", [MuscleGroup.NECK], 30, Position.SITTING),
    Stretch("Tilt head toward shoulder, use hand to gently pull head closer", [MuscleGroup.NECK], 30, Position.SITTING),
    Stretch("Place hand on side of head and gently push head into hand (don't move head)", [MuscleGroup.NECK], 30, Position.SITTING),
    Stretch("Tilt head to one side while pulling the opposite shoulder down", [MuscleGroup.NECK, MuscleGroup.SHOULDERS], 30, Position.SITTING),
    Stretch("Stand in a corner, place hands on walls, lean forward to stretch front of neck", [MuscleGroup.NECK], 30, Position.STANDING),
    Stretch("Move your head in a figure-8 pattern slowly", [MuscleGroup.NECK], 30, Position.SITTING),
    Stretch("Look down and turn head toward your right armpit, hold 15 sec, then left", [MuscleGroup.NECK], 15, Position.SITTING),

    # Shoulder stretches (11-20)
    Stretch("Roll your shoulders backward in big circles 10 times, then forward 10 times", [MuscleGroup.SHOULDERS], 20, Position.SITTING),
    Stretch("Bring right arm across your chest, use left hand to pull it closer, 15 sec each arm", [MuscleGroup.SHOULDERS], 15, Position.SITTING),
    Stretch("Clasp hands behind your back and lift arms away from your body", [MuscleGroup.SHOULDERS, MuscleGroup.CHEST], 20, Position.SITTING),
    Stretch("Raise one arm overhead, bend elbow so hand touches back, pull elbow with other hand, 15 sec each", [MuscleGroup.SHOULDERS, MuscleGroup.ARMS], 15, Position.SITTING),
    Stretch("Stand with back against wall, arms up like goalposts, slide arms up and down 10 times", [MuscleGroup.SHOULDERS, MuscleGroup.UPPER_BACK], 30, Position.STANDING),
    Stretch("Cross arms in front, wrap them around each other, lift elbows up, hold 20 sec each way", [MuscleGroup.SHOULDERS], 20, Position.SITTING),
    Stretch("Place hand on door frame at shoulder height, step forward to stretch chest, 30 sec each side", [MuscleGroup.SHOULDERS, MuscleGroup.CHEST], 30, Position.STANDING),
    Stretch("Raise arm overhead, bend elbow behind head, use other hand to pull elbow, 15 sec each", [MuscleGroup.SHOULDERS, MuscleGroup.ARMS], 15, Position.SITTING),
    Stretch("Reach one arm up and behind back, other arm down and behind, try to touch fingers, 20 sec each", [MuscleGroup.SHOULDERS], 20, Position.STANDING),
    Stretch("Lean forward, let arm hang down, make small circles with hanging arm, 10 each direction", [MuscleGroup.SHOULDERS], 20, Position.STANDING),

    # Chest stretches (21-30)
    Stretch("Stand in doorway, place forearm on frame at shoulder height, step forward, hold 30 sec", [MuscleGroup.CHEST], 30, Position.STANDING),
    Stretch("Stand facing corner, hands on walls at shoulder height, lean into corner for 25 sec", [MuscleGroup.CHEST], 25, Position.STANDING),
    Stretch("Clasp hands behind back, straighten arms and lift up while pushing chest forward", [MuscleGroup.CHEST, MuscleGroup.SHOULDERS], 20, Position.SITTING),
    Stretch("Place one hand on wall at shoulder height, turn body away from wall, 20 sec each side", [MuscleGroup.CHEST], 20, Position.STANDING),
    Stretch("If you have a foam roller, lie on it lengthwise and let arms fall to sides for 45 sec", [MuscleGroup.CHEST], 45, Position.LYING),
    Stretch("Stand or kneel, place hands on lower back, push hips forward and lean back gently", [MuscleGroup.CHEST, MuscleGroup.CORE], 20, Position.STANDING),
    Stretch("Stand sideways to wall, extend arm back to touch wall making a T shape, hold 25 sec", [MuscleGroup.CHEST, MuscleGroup.SHOULDERS], 25, Position.STANDING),
    Stretch("Sit in chair, hold towel behind back with both hands, pull towel to open chest", [MuscleGroup.CHEST], 30, Position.SITTING),
    Stretch("Place palms together behind your back (like reverse prayer), hold 20 seconds", [MuscleGroup.CHEST, MuscleGroup.SHOULDERS], 20, Position.SITTING),
    Stretch("Stand tall, interlace fingers behind back, straighten arms and lift while opening chest", [MuscleGroup.CHEST], 25, Position.STANDING),

    # Upper back stretches (31-40)
    Stretch("Get on hands and knees, arch back up like a cat, then let belly drop down, repeat 10 times", [MuscleGroup.UPPER_BACK, MuscleGroup.LOWER_BACK], 30, Position.LYING),
    Stretch("Kneel and sit back on heels, reach arms forward on floor, hold 30 seconds", [MuscleGroup.UPPER_BACK, MuscleGroup.LOWER_BACK], 30, Position.LYING),
    Stretch("Wrap your arms around yourself in a big hug, round your upper back, hold 20 sec", [MuscleGroup.UPPER_BACK], 20, Position.SITTING),
    Stretch("On hands and knees, slide one arm under your body to the other side, 15 sec each", [MuscleGroup.UPPER_BACK, MuscleGroup.SHOULDERS], 15, Position.LYING),
    Stretch("Sit in chair, lean back over the top of the backrest to arch upper back, hold 20 sec", [MuscleGroup.UPPER_BACK], 20, Position.SITTING),
    Stretch("Sit and turn your upper body to the right, hold chair back, 20 sec each side", [MuscleGroup.UPPER_BACK, MuscleGroup.CORE], 20, Position.SITTING),
    Stretch("Stand with back against wall, raise arms up and down like making snow angels, 15 times", [MuscleGroup.UPPER_BACK], 30, Position.STANDING),
    Stretch("If you have a foam roller, lie on it crosswise under upper back, roll slowly for 1 minute", [MuscleGroup.UPPER_BACK], 60, Position.LYING),
    Stretch("Pull shoulder blades together like squeezing a pencil between them, hold 5 sec, do 10 times", [MuscleGroup.UPPER_BACK], 50, Position.SITTING),
    Stretch("Lie face down, lift arms to make Y, T, and W shapes, 10 times each shape", [MuscleGroup.UPPER_BACK, MuscleGroup.SHOULDERS], 45, Position.LYING),

    # Lower back stretches (41-50)
    Stretch("Lie on back, pull one knee to chest with both hands, hold 20 sec each leg", [MuscleGroup.LOWER_BACK], 20, Position.LYING),
    Stretch("Lie on back, hug both knees to chest, rock gently side to side for 30 sec", [MuscleGroup.LOWER_BACK], 30, Position.LYING),
    Stretch("Lie on back, drop both knees to right side while keeping shoulders down, 25 sec each side", [MuscleGroup.LOWER_BACK, MuscleGroup.CORE], 25, Position.LYING),
    Stretch("Lie face down, push up with arms to lift chest (like a seal), hold 20 seconds", [MuscleGroup.LOWER_BACK, MuscleGroup.CORE], 20, Position.LYING),
    Stretch("Stand and bend forward, let arms hang down toward floor, relax for 30 seconds", [MuscleGroup.LOWER_BACK, MuscleGroup.HAMSTRINGS], 30, Position.STANDING),
    Stretch("Sit with legs straight, reach forward toward your toes, hold 25 sec", [MuscleGroup.LOWER_BACK, MuscleGroup.HAMSTRINGS], 25, Position.SITTING),
    Stretch("Lie on back, place right ankle on left knee, pull left thigh toward chest, 20 sec each", [MuscleGroup.LOWER_BACK, MuscleGroup.HIPS], 20, Position.LYING),
    Stretch("Lie on back, grab behind knees, pull knees apart toward armpits, hold 30 seconds", [MuscleGroup.LOWER_BACK, MuscleGroup.HIPS], 30, Position.LYING),
    Stretch("Lie on back, tighten stomach to press lower back to floor, release, do 15 times", [MuscleGroup.LOWER_BACK, MuscleGroup.CORE], 30, Position.LYING),
    Stretch("On hands and knees, extend right arm forward and left leg back, hold 15 sec, switch", [MuscleGroup.LOWER_BACK, MuscleGroup.CORE], 15, Position.LYING),

    # Arm stretches (51-60)
    Stretch("Raise one arm up, bend elbow so hand goes behind head, pull elbow with other hand, 15 sec each", [MuscleGroup.ARMS], 15, Position.SITTING),
    Stretch("Place palm on door frame behind you at shoulder height, turn body forward, 20 sec each arm", [MuscleGroup.ARMS], 20, Position.STANDING),
    Stretch("Extend arm forward, palm up, pull fingers back toward you with other hand, 15 sec each", [MuscleGroup.ARMS, MuscleGroup.WRISTS], 15, Position.SITTING),
    Stretch("Extend arm forward, palm down, push hand down and back with other hand, 15 sec each", [MuscleGroup.ARMS, MuscleGroup.WRISTS], 15, Position.SITTING),
    Stretch("Put palms together in front of chest (prayer position), lower hands while keeping palms together, 20 sec", [MuscleGroup.ARMS, MuscleGroup.WRISTS], 20, Position.SITTING),
    Stretch("Extend arm across body, use other arm to pull it closer to chest, 15 sec each", [MuscleGroup.ARMS], 15, Position.SITTING),
    Stretch("Put arm behind back, grab wrist with other hand and pull gently, 20 sec each side", [MuscleGroup.ARMS, MuscleGroup.SHOULDERS], 20, Position.SITTING),
    Stretch("Gently pull each finger back one at a time, hold for a few seconds each", [MuscleGroup.WRISTS], 30, Position.SITTING),
    Stretch("Make tight fists, then spread fingers wide, repeat 20 times", [MuscleGroup.ARMS, MuscleGroup.WRISTS], 20, Position.SITTING),
    Stretch("Extend arms to sides, make small circles forward 10 times, then backward 10 times", [MuscleGroup.ARMS, MuscleGroup.SHOULDERS], 20, Position.SITTING),

    # Core stretches (61-70)
    Stretch("Stand and reach one arm overhead, lean to opposite side, feel stretch in side body, 20 sec each", [MuscleGroup.CORE], 20, Position.STANDING),
    Stretch("Sit in chair, turn upper body to right, hold chair back, 15 sec each side", [MuscleGroup.CORE], 15, Position.SITTING),
    Stretch("Lie on back with knees bent, slowly rock knees side to side for 30 seconds", [MuscleGroup.CORE, MuscleGroup.LOWER_BACK], 30, Position.LYING),
    Stretch("Stand with hands on hips, twist upper body left and right, 15 times each way", [MuscleGroup.CORE], 30, Position.STANDING),
    Stretch("Lie face down, straighten arms to lift upper body, keep hips on floor, hold 20 sec", [MuscleGroup.CORE], 20, Position.LYING),
    Stretch("Lie on back, cross right leg over left, drop legs to left side, 25 sec each side", [MuscleGroup.CORE, MuscleGroup.LOWER_BACK], 25, Position.LYING),
    Stretch("Stand with feet wide, touch right hand to left foot, stand up, alternate 10 times each", [MuscleGroup.CORE, MuscleGroup.HAMSTRINGS], 30, Position.STANDING),
    Stretch("Sit and hold arms out, slowly turn body as far right as comfortable, hold 15 sec each side", [MuscleGroup.CORE], 30, Position.SITTING),
    Stretch("Start in push-up position, push hips up and back into inverted V, return, do 10 times", [MuscleGroup.CORE, MuscleGroup.FULL_BODY], 40, Position.LYING),
    Stretch("Stand tall, reach both arms overhead, lean body to make C-shape to right, 20 sec each side", [MuscleGroup.CORE], 20, Position.STANDING),

    # Hip stretches (71-80)
    Stretch("Stand, place right ankle on left knee, sit back like sitting in chair, 20 sec each side", [MuscleGroup.HIPS, MuscleGroup.GLUTES], 20, Position.STANDING),
    Stretch("Sit, place right ankle on left knee, lean chest forward toward shin, 30 sec each side", [MuscleGroup.HIPS], 30, Position.SITTING),
    Stretch("Sit with soles of feet together, knees out to sides, gently press knees down, hold 30 sec", [MuscleGroup.HIPS], 30, Position.SITTING),
    Stretch("Step one foot far back, bend front knee, push hips forward, 25 sec each side", [MuscleGroup.HIPS, MuscleGroup.QUADS], 25, Position.STANDING),
    Stretch("Sit with right leg bent in front, left leg bent behind, lean forward, 20 sec each side", [MuscleGroup.HIPS], 20, Position.SITTING),
    Stretch("Stand with hands on hips, make big circles with your hips, 10 each direction", [MuscleGroup.HIPS], 20, Position.STANDING),
    Stretch("Get on hands and knees, spread knees wide, sit back toward heels, hold 30 seconds", [MuscleGroup.HIPS], 30, Position.LYING),
    Stretch("On hands and knees, lift one knee to side and make circles, 10 each leg", [MuscleGroup.HIPS, MuscleGroup.GLUTES], 30, Position.LYING),
    Stretch("Lie on side, bend knees, keep feet together, open top knee like a clam, hold 15 sec each", [MuscleGroup.HIPS, MuscleGroup.GLUTES], 15, Position.LYING),
    Stretch("Lie on back, cross right ankle over left knee, let right knee fall to side, 20 sec each", [MuscleGroup.HIPS, MuscleGroup.LOWER_BACK], 20, Position.LYING),

    # Leg stretches - Quads & Hamstrings (81-90)
    Stretch("Stand on one leg, bend other knee and hold ankle behind you, pull toward butt, 20 sec each", [MuscleGroup.QUADS], 20, Position.STANDING),
    Stretch("Lie on your side, grab top ankle and pull heel toward butt, 25 sec each side", [MuscleGroup.QUADS], 25, Position.LYING),
    Stretch("Stand and bend forward trying to touch your toes, let arms hang, hold 30 seconds", [MuscleGroup.HAMSTRINGS], 30, Position.STANDING),
    Stretch("Sit with one leg straight, reach toward that foot with both hands, 20 sec each leg", [MuscleGroup.HAMSTRINGS], 20, Position.SITTING),
    Stretch("Lie on back, loop towel around foot, pull leg up keeping it straight, 25 sec each", [MuscleGroup.HAMSTRINGS], 25, Position.LYING),
    Stretch("Place one foot on couch/chair behind you, lunge forward with other leg, 30 sec each", [MuscleGroup.QUADS, MuscleGroup.HIPS], 30, Position.STANDING),
    Stretch("Stand and place heel on desk/table, keep leg straight, lean forward, 20 sec each", [MuscleGroup.HAMSTRINGS], 20, Position.STANDING),
    Stretch("Kneel and sit back on your heels, feel stretch in front of thighs, hold 30 sec", [MuscleGroup.QUADS, MuscleGroup.ANKLES], 30, Position.LYING),
    Stretch("Stand with feet wide apart, bend forward reaching toward floor, hold 30 seconds", [MuscleGroup.HAMSTRINGS, MuscleGroup.HIPS], 30, Position.STANDING),
    Stretch("Stand, cross right leg behind left, lean to left side, feel stretch on outside of right leg, 20 sec each", [MuscleGroup.QUADS, MuscleGroup.HIPS], 20, Position.STANDING),

    # Calves & Ankles (91-100)
    Stretch("Face wall, place hands on it, step one foot back keeping heel down, lean forward, 20 sec each", [MuscleGroup.CALVES], 20, Position.STANDING),
    Stretch("Same as above but bend the back knee slightly to stretch deeper calf, 20 sec each", [MuscleGroup.CALVES], 20, Position.STANDING),
    Stretch("Sit or stand, make circles with your foot at ankle, 10 each way, both feet", [MuscleGroup.ANKLES], 20, Position.SITTING),
    Stretch("Point your toes forward like a ballerina, then pull toes back toward shin, 15 times each foot", [MuscleGroup.ANKLES, MuscleGroup.CALVES], 20, Position.SITTING),
    Stretch("Stand on step with heels hanging off edge, lower heels below step level, raise up, 15 times", [MuscleGroup.CALVES], 30, Position.STANDING),
    Stretch("Lift foot and 'write' the alphabet in the air with your big toe, do both feet", [MuscleGroup.ANKLES], 40, Position.SITTING),
    Stretch("Get in inverted V position (butt up), alternate pressing heels to floor, 30 seconds", [MuscleGroup.CALVES, MuscleGroup.HAMSTRINGS], 30, Position.LYING),
    Stretch("If you have a resistance band, loop it around foot and pull toes toward you, 15 times each", [MuscleGroup.ANKLES], 30, Position.SITTING),
    Stretch("Sit with leg straight, loop towel around ball of foot, pull toward you, 25 sec each", [MuscleGroup.CALVES], 25, Position.SITTING),
    Stretch("Full body flow: Reach up, fold forward, step back to plank, push up, return to standing, 3 times", [MuscleGroup.FULL_BODY], 60, Position.STANDING),
]

# 100 Unique Exercises with muscle groups (all time-based)
EXERCISES = [
    # Lower body exercises (1-25)
    Exercise("Stand with feet shoulder-width apart, sit back like sitting in chair, stand up continuously", [MuscleGroup.QUADS, MuscleGroup.GLUTES], 1, Position.STANDING),
    Exercise("Do squats with a jump up as you stand, land softly", [MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.CALVES], 2, Position.STANDING),
    Exercise("Step forward into lunges, knee at 90 degrees, push back up, alternate legs", [MuscleGroup.QUADS, MuscleGroup.GLUTES], 1, Position.STANDING),
    Exercise("Step backward into lunges instead of forward, alternate legs", [MuscleGroup.QUADS, MuscleGroup.GLUTES], 1, Position.STANDING),
    Exercise("Step sideways and bend that knee while keeping other leg straight, alternate sides", [MuscleGroup.QUADS, MuscleGroup.HIPS], 2, Position.STANDING),
    Exercise("Put one foot on chair behind you, squat down on front leg, switch legs halfway", [MuscleGroup.QUADS, MuscleGroup.GLUTES], 2, Position.STANDING),
    Exercise("Stand on one leg, hinge forward at hips reaching toward floor, return to standing, alternate", [MuscleGroup.HAMSTRINGS, MuscleGroup.GLUTES, MuscleGroup.CORE], 2, Position.STANDING),
    Exercise("Lean back against wall, slide down until thighs parallel to floor and hold", [MuscleGroup.QUADS], 2, Position.STANDING),
    Exercise("Stand and rise up on your toes, lower back down continuously", [MuscleGroup.CALVES], 1, Position.STANDING),
    Exercise("Stand on one foot and rise up on toes, switch legs every few reps", [MuscleGroup.CALVES], 2, Position.STANDING),
    Exercise("Lie on back, feet flat, lift hips up to make straight line from knees to shoulders", [MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS], 1, Position.LYING),
    Exercise("Lie on back, lift hips while extending one leg straight out, alternate legs", [MuscleGroup.GLUTES, MuscleGroup.CORE], 2, Position.LYING),
    Exercise("Lie on side with knees bent, keep feet together, open top knee like a clam", [MuscleGroup.GLUTES, MuscleGroup.HIPS], 1, Position.LYING),
    Exercise("Get on hands and knees, kick one leg straight back and up, alternate legs", [MuscleGroup.GLUTES], 1, Position.LYING),
    Exercise("On hands and knees, lift knee to side like a dog at hydrant, alternate legs", [MuscleGroup.GLUTES, MuscleGroup.HIPS], 1, Position.LYING),
    Exercise("Step up onto chair with one foot, bring other knee up, step down, alternate", [MuscleGroup.QUADS, MuscleGroup.GLUTES], 2, Position.STANDING),
    Exercise("Jump with both feet onto a sturdy surface like a step, step down carefully", [MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.CALVES], 3, Position.STANDING),
    Exercise("Squat on one leg while other leg extends forward, use wall for balance, alternate", [MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.CORE], 3, Position.STANDING),
    Exercise("Stand and lift leg straight out to the side, keep body straight, alternate sides", [MuscleGroup.HIPS, MuscleGroup.GLUTES], 1, Position.STANDING),
    Exercise("Stand and bring knee up toward chest, march in place", [MuscleGroup.HIPS, MuscleGroup.CORE], 1, Position.STANDING),
    Exercise("Step one leg behind and across the other into a curtsy position, alternate sides", [MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.HIPS], 2, Position.STANDING),
    Exercise("Get in squat position, do small up-down bounces without fully standing", [MuscleGroup.QUADS, MuscleGroup.GLUTES], 2, Position.STANDING),
    Exercise("Take alternating lunge steps forward as you walk across room", [MuscleGroup.QUADS, MuscleGroup.GLUTES], 1, Position.STANDING),
    Exercise("Stand with feet wide and toes pointed out, squat down and up", [MuscleGroup.QUADS, MuscleGroup.HIPS], 1, Position.STANDING),
    Exercise("Jump from lunge on one side to lunge on other side", [MuscleGroup.QUADS, MuscleGroup.GLUTES], 3, Position.STANDING),

    # Upper body exercises (26-50)
    Exercise("Get in plank position, lower chest to floor by bending arms, push back up", [MuscleGroup.CHEST, MuscleGroup.ARMS, MuscleGroup.SHOULDERS], 2, Position.LYING),
    Exercise("Place hands on desk edge, do push-ups at an angle (easier than floor)", [MuscleGroup.CHEST, MuscleGroup.ARMS], 1, Position.STANDING),
    Exercise("Do push-ups with hands placed wider than shoulders", [MuscleGroup.CHEST], 2, Position.LYING),
    Exercise("Make a diamond shape with hands (thumbs and index fingers touch), do push-ups", [MuscleGroup.CHEST, MuscleGroup.ARMS], 3, Position.LYING),
    Exercise("Put feet on chair/couch, hands on floor, do push-ups in this position", [MuscleGroup.CHEST, MuscleGroup.SHOULDERS], 3, Position.LYING),
    Exercise("Sit on edge of chair, hands next to hips, slide forward and dip down, push back up", [MuscleGroup.ARMS], 2, Position.SITTING),
    Exercise("Do push-ups with hands close together under chest", [MuscleGroup.ARMS, MuscleGroup.CHEST], 2, Position.LYING),
    Exercise("Get in inverted V position (butt high), lower head toward floor bending arms, push back up", [MuscleGroup.SHOULDERS, MuscleGroup.ARMS], 2, Position.LYING),
    Exercise("Extend arms to sides, make big circles forward then backward", [MuscleGroup.SHOULDERS], 1, Position.STANDING),
    Exercise("Raise straight arms out to sides to shoulder height, lower down", [MuscleGroup.SHOULDERS], 1, Position.STANDING),
    Exercise("Raise straight arms forward to shoulder height, lower down", [MuscleGroup.SHOULDERS], 1, Position.STANDING),
    Exercise("In plank position, tap right hand to left shoulder, then left to right", [MuscleGroup.SHOULDERS, MuscleGroup.CORE], 2, Position.LYING),
    Exercise("Lie face down, lift chest and legs off floor like flying, hold briefly and repeat", [MuscleGroup.LOWER_BACK, MuscleGroup.GLUTES], 1, Position.LYING),
    Exercise("Lie face down, lift chest, move arms like making snow angels backward", [MuscleGroup.UPPER_BACK, MuscleGroup.SHOULDERS], 1, Position.LYING),
    Exercise("Face wall, walk feet up wall while walking hands closer to wall", [MuscleGroup.SHOULDERS, MuscleGroup.CORE, MuscleGroup.ARMS], 3, Position.STANDING),
    Exercise("Lie face down, lift arms to make Y shape, then T, then W, repeat sequence", [MuscleGroup.UPPER_BACK, MuscleGroup.SHOULDERS], 2, Position.LYING),
    Exercise("Lie under sturdy desk/table, pull yourself up using edge", [MuscleGroup.ARMS, MuscleGroup.UPPER_BACK], 2, Position.LYING),
    Exercise("Press palms together hard in front of chest", [MuscleGroup.CHEST], 1, Position.SITTING),
    Exercise("Hold arms out to sides, make tiny circles", [MuscleGroup.ARMS, MuscleGroup.SHOULDERS], 1, Position.SITTING),
    Exercise("In plank, push shoulder blades apart then squeeze together, keep arms straight", [MuscleGroup.UPPER_BACK, MuscleGroup.SHOULDERS], 2, Position.LYING),
    Exercise("Stand, keep legs straight, bend forward at hips keeping back straight, return up", [MuscleGroup.LOWER_BACK, MuscleGroup.HAMSTRINGS], 1, Position.STANDING),
    Exercise("On hands and knees, extend right arm forward and left leg back, hold briefly, switch", [MuscleGroup.LOWER_BACK, MuscleGroup.CORE], 1, Position.LYING),
    Exercise("Do push-ups with one hand slightly ahead of the other, switch hand positions halfway", [MuscleGroup.CHEST, MuscleGroup.ARMS], 2, Position.LYING),
    Exercise("From plank, push hips up and back to inverted V, return to plank", [MuscleGroup.ARMS, MuscleGroup.SHOULDERS, MuscleGroup.CORE], 2, Position.LYING),
    Exercise("Start in plank, push hips up, lower chest toward floor in scooping motion, return", [MuscleGroup.CHEST, MuscleGroup.SHOULDERS, MuscleGroup.ARMS], 3, Position.LYING),

    # Core exercises (51-75)
    Exercise("Hold push-up position with straight body from head to heels", [MuscleGroup.CORE], 2, Position.LYING),
    Exercise("Lie on side, prop up on elbow, lift hips off floor", [MuscleGroup.CORE], 2, Position.LYING),
    Exercise("In plank, bring knees toward chest alternating quickly like running", [MuscleGroup.CORE, MuscleGroup.SHOULDERS], 2, Position.LYING),
    Exercise("Lie on back, bring elbow to opposite knee alternating like pedaling bike", [MuscleGroup.CORE], 1, Position.LYING),
    Exercise("Sit with knees bent, lean back slightly, rotate side to side touching floor", [MuscleGroup.CORE], 2, Position.SITTING),
    Exercise("Lie on back, keep legs straight, lift them up and down without touching floor", [MuscleGroup.CORE, MuscleGroup.HIPS], 2, Position.LYING),
    Exercise("Lie on back, kick legs up and down alternately like swimming", [MuscleGroup.CORE, MuscleGroup.HIPS], 2, Position.LYING),
    Exercise("Lie on back, legs up, cross right over left then left over right", [MuscleGroup.CORE, MuscleGroup.HIPS], 2, Position.LYING),
    Exercise("Lie on back, arms up, lower opposite arm and leg slowly, return, alternate", [MuscleGroup.CORE], 1, Position.LYING),
    Exercise("Lie on back, lift shoulders and legs off floor, hold body like a boat", [MuscleGroup.CORE], 3, Position.LYING),
    Exercise("Lie on back, reach up to touch toes bringing legs and torso up together", [MuscleGroup.CORE], 3, Position.LYING),
    Exercise("In plank, jump feet apart and together like jumping jacks", [MuscleGroup.CORE, MuscleGroup.SHOULDERS], 2, Position.LYING),
    Exercise("On hands and knees, crawl forward keeping knees just off floor, then back", [MuscleGroup.CORE, MuscleGroup.SHOULDERS], 2, Position.LYING),
    Exercise("Run in place bringing knees up high to waist level", [MuscleGroup.CORE, MuscleGroup.QUADS], 1, Position.STANDING),
    Exercise("Run in place kicking heels up to touch butt", [MuscleGroup.CORE, MuscleGroup.HAMSTRINGS], 1, Position.STANDING),
    Exercise("Stand, bring knee up to side while crunching elbow down, alternate sides", [MuscleGroup.CORE], 1, Position.STANDING),
    Exercise("Stand, swing arms diagonally from low to high like chopping wood, alternate sides", [MuscleGroup.CORE], 1, Position.STANDING),
    Exercise("From plank on hands, lower to elbows one at a time, then back up", [MuscleGroup.CORE, MuscleGroup.ARMS], 2, Position.LYING),
    Exercise("In side plank, lower hip to floor and lift back up", [MuscleGroup.CORE], 2, Position.LYING),
    Exercise("Lie on back, legs up, slowly lower legs to right then left like windshield wipers", [MuscleGroup.CORE], 3, Position.LYING),
    Exercise("Lie on back, reach up trying to touch your toes", [MuscleGroup.CORE], 1, Position.LYING),
    Exercise("Lie on back, bring knees to chest lifting hips off floor", [MuscleGroup.CORE], 2, Position.LYING),
    Exercise("Side plank with top arm and leg extended like a star", [MuscleGroup.CORE, MuscleGroup.SHOULDERS], 3, Position.LYING),
    Exercise("In plank, lift one leg straight up, hold briefly, alternate legs", [MuscleGroup.CORE, MuscleGroup.GLUTES], 2, Position.LYING),
    Exercise("Stand, bring knee up while bringing opposite elbow down to meet it, alternate", [MuscleGroup.CORE], 1, Position.STANDING),

    # Full body/Cardio exercises (76-100)
    Exercise("Squat, place hands on floor, jump feet back to plank, do push-up, jump feet in, stand", [MuscleGroup.FULL_BODY], 3, Position.STANDING),
    Exercise("Jump with feet apart while raising arms overhead, jump feet together arms down", [MuscleGroup.FULL_BODY], 1, Position.STANDING),
    Exercise("Jump spreading arms and legs wide like a star", [MuscleGroup.FULL_BODY], 2, Position.STANDING),
    Exercise("From standing, squat and kick legs back to plank, jump feet back in, stand", [MuscleGroup.FULL_BODY], 2, Position.STANDING),
    Exercise("Jump sideways landing on one foot, immediately jump to other side, like ice skating", [MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.CORE], 2, Position.STANDING),
    Exercise("Throw punches in the air like boxing - jabs, hooks, uppercuts", [MuscleGroup.ARMS, MuscleGroup.SHOULDERS, MuscleGroup.CORE], 1, Position.STANDING),
    Exercise("Jump in place as if using a jump rope (no rope needed)", [MuscleGroup.CALVES, MuscleGroup.SHOULDERS], 1, Position.STANDING),
    Exercise("Jump crossing feet in front and behind alternately while moving arms", [MuscleGroup.FULL_BODY], 1, Position.STANDING),
    Exercise("Jump with arms moving horizontally like clapping in front and behind", [MuscleGroup.SHOULDERS, MuscleGroup.CHEST], 1, Position.STANDING),
    Exercise("Jump bringing knees up toward chest as high as possible", [MuscleGroup.QUADS, MuscleGroup.CORE], 3, Position.STANDING),
    Exercise("Jump forward as far as you can from standing, walk back and repeat", [MuscleGroup.QUADS, MuscleGroup.GLUTES], 2, Position.STANDING),
    Exercise("Jump sideways back and forth over an imaginary line", [MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.CORE], 2, Position.STANDING),
    Exercise("Get on hands and knees, lift knees slightly off floor, hold position", [MuscleGroup.FULL_BODY], 2, Position.LYING),
    Exercise("Sit on floor, hands behind you, lift hips and walk like a crab", [MuscleGroup.ARMS, MuscleGroup.CORE, MuscleGroup.GLUTES], 2, Position.SITTING),
    Exercise("Stand, bend to touch floor, walk hands forward to plank, walk hands back, stand", [MuscleGroup.FULL_BODY], 2, Position.STANDING),
    Exercise("Squat low, jump forward staying in squat position", [MuscleGroup.QUADS, MuscleGroup.GLUTES], 2, Position.STANDING),
    Exercise("Jump side to side in a speed skating motion, swing arms across body", [MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.CORE], 2, Position.STANDING),
    Exercise("Skip in place driving knee up high with each skip", [MuscleGroup.QUADS, MuscleGroup.CALVES], 1, Position.STANDING),
    Exercise("Punch, kick, knee strike combinations like kickboxing", [MuscleGroup.FULL_BODY], 2, Position.STANDING),
    Exercise("Run in place as fast as you can", [MuscleGroup.FULL_BODY], 2, Position.STANDING),
    Exercise("Jump forward as far as possible, then quickly run backward to start, repeat", [MuscleGroup.QUADS, MuscleGroup.GLUTES], 2, Position.STANDING),
    Exercise("Stand on one foot, try to balance without wobbling, switch legs halfway", [MuscleGroup.CORE, MuscleGroup.ANKLES], 1, Position.STANDING),
    Exercise("Stand on one foot, place other foot sole against inner thigh, hands together at chest", [MuscleGroup.CORE, MuscleGroup.HIPS], 1, Position.STANDING),
    Exercise("From lying down, stand up using only one arm and leg, then lie back down, alternate sides", [MuscleGroup.FULL_BODY], 3, Position.LYING),
    Exercise("From standing, quickly drop to plank position, jump feet back in, stand", [MuscleGroup.FULL_BODY], 2, Position.STANDING),
]


def filter_exercises_by_position(exercises: List[Exercise], position_preference: str) -> List[Exercise]:
    """Filter exercises based on position preference."""
    if position_preference == "all":
        return exercises
    elif position_preference == "sitting_standing":
        return [e for e in exercises if e.position in [Position.SITTING, Position.STANDING]]
    elif position_preference == "sitting":
        return [e for e in exercises if e.position == Position.SITTING]
    elif position_preference == "standing":
        return [e for e in exercises if e.position == Position.STANDING]
    elif position_preference == "lying":
        return [e for e in exercises if e.position == Position.LYING]
    else:
        # Default to sitting and standing if unknown preference
        return [e for e in exercises if e.position in [Position.SITTING, Position.STANDING]]


def filter_stretches_by_position(stretches: List[Stretch], position_preference: str) -> List[Stretch]:
    """Filter stretches based on position preference."""
    if position_preference == "all":
        return stretches
    elif position_preference == "sitting_standing":
        return [s for s in stretches if s.position in [Position.SITTING, Position.STANDING]]
    elif position_preference == "sitting":
        return [s for s in stretches if s.position == Position.SITTING]
    elif position_preference == "standing":
        return [s for s in stretches if s.position == Position.STANDING]
    elif position_preference == "lying":
        return [s for s in stretches if s.position == Position.LYING]
    else:
        # Default to sitting and standing if unknown preference
        return [s for s in stretches if s.position in [Position.SITTING, Position.STANDING]]

# 100 Unique Motivational Messages
MOTIVATIONS = [
    # Achievement & Progress (1-20)
    "Every stretch brings you closer to your healthiest self!",
    "Small movements today, big improvements tomorrow!",
    "You're investing in a lifetime of better health right now!",
    "Champions take breaks - you're building sustainable success!",
    "This moment of movement is a gift to your future self!",
    "Progress happens one stretch at a time - keep going!",
    "You're literally adding years to your life with these breaks!",
    "Excellence includes knowing when to pause and recharge!",
    "Every rep counts toward a stronger, healthier you!",
    "You're not just exercising, you're building better habits!",
    "Today's discomfort is tomorrow's strength!",
    "You're proving that health is your priority - well done!",
    "Each movement is a vote for the person you want to become!",
    "Success is built on consistent small actions like this!",
    "You're crushing your wellness goals one break at a time!",
    "Your body will thank you for this in 10 years!",
    "This is what taking control of your health looks like!",
    "You're literally becoming stronger with every movement!",
    "Future you is cheering for present you right now!",
    "You're building an unbreakable foundation of health!",

    # Energy & Productivity (21-40)
    "Movement is the secret to sustained energy all day!",
    "You're supercharging your brain with fresh oxygen!",
    "This break will make your next work session 10x better!",
    "Active breaks = sharper focus. You're doing it right!",
    "You're unlocking your afternoon productivity boost!",
    "Movement is your natural energy drink - no crash later!",
    "You're preventing that 3pm slump before it happens!",
    "Your brain loves when you move - it's science!",
    "You're literally increasing your IQ with this movement!",
    "This is your secret weapon for all-day mental clarity!",
    "You're activating your body's natural focus enhancer!",
    "Movement breaks = creativity breaks. Genius incoming!",
    "You're charging your mental batteries the right way!",
    "Your productivity just went up 20% with this break!",
    "You're giving your brain the fuel it craves!",
    "This movement is worth 2 cups of coffee in energy!",
    "You're optimizing your performance like a pro athlete!",
    "Your neurons are celebrating this movement break!",
    "You're unlocking your brain's full potential right now!",
    "This break is your competitive advantage at work!",

    # Self-Care & Mindfulness (41-60)
    "You deserve this moment of self-care!",
    "Listening to your body's needs shows true wisdom!",
    "You're honoring your body with this movement!",
    "This is self-love in action - be proud!",
    "You're choosing wellness over burnout - smart move!",
    "Your body is your lifelong home - you're maintaining it well!",
    "You're practicing radical self-care and it shows!",
    "This break is an act of self-respect!",
    "You're proving that your health matters!",
    "Taking breaks is strength, not weakness!",
    "You're modeling healthy behavior for everyone around you!",
    "Your commitment to wellness is inspiring!",
    "This is what putting yourself first looks like!",
    "You're breaking the cycle of endless sitting!",
    "Your future self will remember this kindness!",
    "You're choosing long-term health over short-term comfort!",
    "This movement is a celebration of what your body can do!",
    "You're writing a new story of health and vitality!",
    "Your body is grateful for this attention!",
    "You're proving that busy people can still prioritize health!",

    # Encouragement & Positivity (61-80)
    "You've got this! Every movement matters!",
    "Look at you, taking charge of your health!",
    "You're stronger than you think - keep moving!",
    "Your consistency is paying off big time!",
    "You're absolutely crushing these movement goals!",
    "Every stretch is a win - celebrate it!",
    "You're building momentum with every break!",
    "Your dedication is remarkable - keep it up!",
    "You're making healthy look easy!",
    "This is exactly what success looks like!",
    "You're an inspiration to everyone around you!",
    "Your body is becoming more capable every day!",
    "You're proving that small actions create big changes!",
    "Look at you, prioritizing what really matters!",
    "You're unstoppable when you move like this!",
    "Your commitment to movement is admirable!",
    "You're showing up for yourself - that's powerful!",
    "Every break you take is a victory lap!",
    "You're redefining what's possible for your health!",
    "Your positive choices are compounding daily!",

    # Science & Facts (81-100)
    "Studies show movement breaks increase lifespan by 20%!",
    "You're reducing your disease risk by 40% with regular movement!",
    "This break is improving your posture for the next 2 hours!",
    "You just boosted your metabolism for the next hour!",
    "Your cardiovascular system is celebrating this movement!",
    "You're increasing bone density with every weight-bearing move!",
    "This movement is releasing endorphins - natural happiness!",
    "You're improving your balance and preventing future falls!",
    "Your immune system gets stronger with regular movement!",
    "You just reduced your stress hormones significantly!",
    "This break is improving your insulin sensitivity!",
    "You're literally growing new brain cells with this exercise!",
    "Your joints stay young with regular movement like this!",
    "You just increased blood flow to your brain by 15%!",
    "This movement is protecting your DNA from aging!",
    "You're reducing inflammation throughout your body!",
    "Your lymphatic system is thanking you for this movement!",
    "You just triggered your body's repair mechanisms!",
    "This break is optimizing your hormone production!",
    "You're actively preventing 13 types of cancer with regular movement!"
]

# Benefits linked to muscle groups
MUSCLE_GROUP_BENEFITS = {
    MuscleGroup.NECK: [
        "Reduced tension headaches and migraine frequency",
        "Improved posture and spinal alignment",
        "Better sleep quality from released neck tension",
        "Enhanced focus from improved blood flow to brain",
        "Decreased risk of cervical spine issues",
        "Relief from tech neck syndrome",
        "Improved range of motion for daily activities",
        "Reduced jaw tension and TMJ symptoms",
        "Better breathing from aligned airways",
        "Prevention of chronic neck pain",
    ],
    MuscleGroup.SHOULDERS: [
        "Increased upper body strength and endurance",
        "Better posture reducing back pain",
        "Improved ability to lift and carry",
        "Reduced risk of rotator cuff injuries",
        "Enhanced athletic performance",
        "Greater functional movement in daily life",
        "Decreased shoulder impingement risk",
        "Better desk posture reducing strain",
        "Improved overhead reaching ability",
        "Prevention of frozen shoulder syndrome",
    ],
    MuscleGroup.CHEST: [
        "Improved breathing capacity and lung function",
        "Better posture countering forward shoulder roll",
        "Increased upper body pushing strength",
        "Enhanced athletic performance",
        "Reduced risk of muscle imbalances",
        "Better heart health from chest opening",
        "Improved confidence from open posture",
        "Greater functional strength for daily tasks",
        "Prevention of tight chest syndrome",
        "Enhanced ribcage mobility",
    ],
    MuscleGroup.UPPER_BACK: [
        "Dramatically improved posture",
        "Reduced upper back pain and tension",
        "Better shoulder blade stability",
        "Enhanced breathing from thoracic mobility",
        "Decreased risk of kyphosis (hunched back)",
        "Improved desk ergonomics",
        "Better spinal health overall",
        "Reduced referred pain to arms",
        "Enhanced athletic performance",
        "Prevention of chronic upper back issues",
    ],
    MuscleGroup.LOWER_BACK: [
        "Significant reduction in lower back pain",
        "Improved core stability and strength",
        "Better posture throughout the day",
        "Enhanced ability to lift safely",
        "Reduced risk of disc herniation",
        "Improved balance and coordination",
        "Better pelvic alignment",
        "Decreased sciatic nerve pain",
        "Enhanced functional movement",
        "Prevention of chronic back conditions",
    ],
    MuscleGroup.ARMS: [
        "Increased grip strength for daily tasks",
        "Better arm definition and tone",
        "Reduced risk of repetitive strain injuries",
        "Improved typing and computer work endurance",
        "Enhanced ability to carry and lift",
        "Better circulation to hands and fingers",
        "Reduced risk of carpal tunnel syndrome",
        "Improved fine motor skills",
        "Greater functional independence",
        "Prevention of tennis/golfer's elbow",
    ],
    MuscleGroup.CORE: [
        "Dramatically improved posture all day",
        "Significant reduction in back pain",
        "Better balance and stability",
        "Enhanced athletic performance",
        "Improved digestion from core strength",
        "Reduced risk of falls and injuries",
        "Better breathing from diaphragm support",
        "Flatter, stronger midsection",
        "Improved functional movement",
        "Enhanced overall body strength",
    ],
    MuscleGroup.HIPS: [
        "Increased mobility and flexibility",
        "Reduced lower back pain",
        "Better walking and running mechanics",
        "Improved balance and stability",
        "Decreased risk of hip replacement",
        "Enhanced athletic performance",
        "Better pelvic floor health",
        "Reduced knee pain from hip alignment",
        "Improved sexual health",
        "Prevention of hip bursitis",
    ],
    MuscleGroup.GLUTES: [
        "Powerful lower body strength",
        "Significant reduction in back pain",
        "Improved posture and spine alignment",
        "Better athletic performance",
        "Enhanced metabolism from muscle mass",
        "Reduced knee pain from proper mechanics",
        "Improved hip stability",
        "Better stair climbing ability",
        "Enhanced running efficiency",
        "Prevention of hip and back issues",
    ],
    MuscleGroup.QUADS: [
        "Increased leg strength and power",
        "Better knee joint protection",
        "Improved ability to stand from sitting",
        "Enhanced walking and running endurance",
        "Reduced risk of falls",
        "Better athletic performance",
        "Improved metabolism from large muscle mass",
        "Enhanced stair climbing ability",
        "Better balance and stability",
        "Prevention of knee osteoarthritis",
    ],
    MuscleGroup.HAMSTRINGS: [
        "Reduced lower back pain",
        "Better running speed and power",
        "Improved posture from posterior chain",
        "Decreased risk of hamstring injuries",
        "Better knee joint stability",
        "Enhanced athletic performance",
        "Improved hip mobility",
        "Better deadlifting mechanics",
        "Reduced risk of ACL injuries",
        "Enhanced jumping ability",
    ],
    MuscleGroup.CALVES: [
        "Better balance and stability",
        "Improved circulation in lower legs",
        "Enhanced walking and running efficiency",
        "Reduced risk of ankle injuries",
        "Better jumping ability",
        "Improved venous return reducing swelling",
        "Enhanced athletic performance",
        "Better foot arch support",
        "Reduced risk of plantar fasciitis",
        "Prevention of deep vein thrombosis",
    ],
    MuscleGroup.WRISTS: [
        "Prevention of carpal tunnel syndrome",
        "Reduced typing-related pain",
        "Better grip strength",
        "Improved fine motor control",
        "Reduced risk of tendonitis",
        "Better circulation to hands",
        "Enhanced range of motion",
        "Reduced arthritis symptoms",
        "Better hand functionality",
        "Prevention of repetitive strain injuries",
    ],
    MuscleGroup.ANKLES: [
        "Significantly reduced ankle sprain risk",
        "Better balance and proprioception",
        "Improved walking and running mechanics",
        "Enhanced athletic performance",
        "Better circulation to feet",
        "Reduced risk of falls",
        "Improved foot arch support",
        "Better jumping and landing mechanics",
        "Prevention of Achilles tendon issues",
        "Enhanced mobility for life",
    ],
    MuscleGroup.FULL_BODY: [
        "Complete cardiovascular health improvement",
        "Total body strength and endurance",
        "Optimal metabolic function",
        "Comprehensive injury prevention",
        "Maximum calorie burn",
        "Full-body coordination improvement",
        "Enhanced overall athleticism",
        "Complete postural alignment",
        "Whole-body flexibility gains",
        "Systemic health optimization",
    ],
}

def get_benefits_for_muscle_groups(muscle_groups: List[MuscleGroup]) -> List[str]:
    """Get relevant benefits for the given muscle groups"""
    benefits = []
    for mg in muscle_groups:
        if mg in MUSCLE_GROUP_BENEFITS:
            benefits.extend(MUSCLE_GROUP_BENEFITS[mg])
    return list(set(benefits))  # Remove duplicates