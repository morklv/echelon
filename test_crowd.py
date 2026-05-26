from app.cv.crowd_analysis import analyze_crowd
# imports crowd/vehicle scene analyzer


result = analyze_crowd("test_images/fourth_test.jpg")
# runs crowd analysis on test image


print(result)
# prints result in terminal