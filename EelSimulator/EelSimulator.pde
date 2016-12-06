/*

  Eel Simulator and Lighter
  
  1. Simulator: draws eel shape on the monitor
  2. Lighter: sends data to the lights
  
  5/10/16
  
  A. Better morphing included only in the Processing component 
  
  Built on glorious Rose Simulator
  
  x,y coordinates are s,p (strip, pixel) coordinates.
    
*/

int LEDS = 144;
byte STRIPS = 2;
byte SEGMENT = 12;  // How many pixels per segment
byte numEels = 24;  // Number of Eels

byte[] eel_size_map = { 12, 12 };  // Segments in each eel
char[] eel_direct_map = { 'F', 'F' };  // Directionality of each eel

import com.heroicrobot.dropbit.registry.*;
import com.heroicrobot.dropbit.devices.pixelpusher.Pixel;
import com.heroicrobot.dropbit.devices.pixelpusher.Strip;
import com.heroicrobot.dropbit.devices.pixelpusher.PixelPusher;
import com.heroicrobot.dropbit.devices.pixelpusher.PusherCommand;

import processing.net.*;
import java.util.*;
import java.util.regex.*;
import java.awt.Color;

// network vars
int port = 4444;
Server _server; 
StringBuffer _buf = new StringBuffer();

class TestObserver implements Observer {
  public boolean hasStrips = false;
  public void update(Observable registry, Object updatedDevice) {
    println("Registry changed!");
    if (updatedDevice != null) {
      println("Device change: " + updatedDevice);
    }
    this.hasStrips = true;
  }
}

TestObserver testObserver;

// Physical strip registry
DeviceRegistry registry;
List<Strip> strips = new ArrayList<Strip>();

//
// Controller on the bottom of the screen
//
boolean DRAW_LABELS = false;

int BRIGHTNESS = 100;  // A percentage
int SATURATION = 0;    // 0 - 255
int COLOR_STATE = 0;   // no enum types in processing. Messy

int delay_time = 10000;  // delay time length in milliseconds (dummy initial value)
int start_time = millis();  // start time point (in absolute time)
int last_time = start_time;

// Color buffers: [strip][pixel][r,g,b]
// Several buffers permits updating only the lights that change color
// May improve performance and reduce flickering
char[][][] curr_buffer = new char[STRIPS][LEDS][3];
char[][][] next_buffer = new char[STRIPS][LEDS][3];
char[][][] morph_buffer = new char[STRIPS][LEDS][3];

// Calculated pixel constants for simulator display
boolean UPDATE_VISUALIZER = false;  // turn false for LED-only updates
int SCREEN_SIZE = 500;  // This is the value to change for Screen Size
int SCREEN_WIDTH = SCREEN_SIZE;
float BORDER = 0.05; // How much fractional edge between eel and screen
int BORDER_PIX = int(SCREEN_SIZE * BORDER); // Edge in pixels

//
//  Setup
// 
void setup() {
  
  size(SCREEN_WIDTH, SCREEN_WIDTH + 50); // 50 for controls
  colorMode(RGB, 255);
  
  frameRate(20);
  
  registry = new DeviceRegistry();
  testObserver = new TestObserver();
  registry.addObserver(testObserver);
  prepareExitHandler();
  strips = registry.getStrips();
  
  initializeColorBuffers();  // Stuff with zeros (all black)
  
  _server = new Server(this, port);
  println("server listening:" + _server);
  
  background(200);
}

void draw() {
  drawBottomControls();
  pollServer();        // Get messages from python show runner
  update_morph();
}

void drawGrids() {
  for (int i = 0; i < numEels; i++) {
     draw_grid(i);
  }
}

// Drawing the eel grid
void draw_grid(int eel_num) {
  color black = color(0,0,0);
}

void drawCheckbox(int x, int y, int size, color fill, boolean checked) {
  stroke(0);
  fill(fill);  
  rect(x,y,size,size);
  if (checked) {    
    line(x,y,x+size,y+size);
    line(x+size,y,x,y+size);
  }  
}

void drawBottomControls() {
  // draw a bottom white region
  fill(255,255,255);  // White
  rect(0,SCREEN_SIZE,SCREEN_WIDTH,40);
  
  // draw divider lines
  stroke(0);
  line(90,SCREEN_SIZE,90,SCREEN_SIZE+40);
  line(240,SCREEN_SIZE,240,SCREEN_SIZE+40);
  line(420,SCREEN_SIZE,420,SCREEN_SIZE+40);
  line(560,SCREEN_SIZE,560,SCREEN_SIZE+40);
  
  // draw checkboxes
  stroke(0);
  fill(255,255,255);  // White
  
  drawCheckbox(10,SCREEN_SIZE+10,20, color(255,255,255), DRAW_LABELS);  // label checkbox
  
  rect(150,SCREEN_SIZE+4,15,15);  // minus brightness
  rect(150,SCREEN_SIZE+22,15,15);  // plus brightness
  
  rect(470,SCREEN_SIZE+4,15,15);  // minus saturation
  rect(470,SCREEN_SIZE+22,15,15);  // plus saturation
  
  drawCheckbox(290,SCREEN_SIZE+4,15, color(255,0,0), COLOR_STATE == 1);
  drawCheckbox(290,SCREEN_SIZE+22,15, color(255,0,0), COLOR_STATE == 4);
  drawCheckbox(310,SCREEN_SIZE+4,15, color(0,255,0), COLOR_STATE == 2);
  drawCheckbox(310,SCREEN_SIZE+22,15, color(0,255,0), COLOR_STATE == 5);
  drawCheckbox(330,SCREEN_SIZE+4,15, color(0,0,255), COLOR_STATE == 3);
  drawCheckbox(330,SCREEN_SIZE+22,15, color(0,0,255), COLOR_STATE == 6);
  drawCheckbox(350,SCREEN_SIZE+10,20, color(255,255,255), COLOR_STATE == 0);
    
  // draw text labels in 12-point Helvetica
  fill(0);
  textAlign(LEFT);
  PFont f = createFont("Helvetica", 12, true);
  textFont(f, 12);  
  text("Labels", 40, SCREEN_SIZE+25);
  
  text("-", 140, SCREEN_SIZE+16);
  text("+", 140, SCREEN_SIZE+34);
  text("Brightness", 175, SCREEN_SIZE+25);
  textFont(f, 20);
  text(BRIGHTNESS, 100, SCREEN_SIZE+28);
  
  textFont(f, 12);
  text("-", 460, SCREEN_SIZE+16);
  text("+", 460, SCREEN_SIZE+34);
  text("Saturation", 495, SCREEN_SIZE+25);
  textFont(f, 20);
  text(SATURATION, 430, SCREEN_SIZE+28);
  
  textFont(f, 12);
  text("None", 255, SCREEN_SIZE+16);
  text("All", 268, SCREEN_SIZE+34);
  text("Color", 380, SCREEN_SIZE+25);
  
  int font_size = 12;  // default size
  f = createFont("Helvetica", font_size, true);
  textFont(f, font_size);
}

void mouseClicked() {  
  //println("click! x:" + mouseX + " y:" + mouseY);
  if (mouseX > 20 && mouseX < 40 && mouseY > SCREEN_SIZE+10 && mouseY < SCREEN_SIZE+30) {
    // clicked draw labels button
    DRAW_LABELS = !DRAW_LABELS;
   
  }  else if (mouseX > 200 && mouseX < 215 && mouseY > SCREEN_SIZE+4 && mouseY < SCREEN_SIZE+19) {
    
    // Bright down checkbox  
    BRIGHTNESS -= 5;
    if (BRIGHTNESS < 1) BRIGHTNESS = 1;
   
    // Bright up checkbox
  } else if (mouseX > 200 && mouseX < 215 && mouseY > SCREEN_SIZE+22 && mouseY < SCREEN_SIZE+37) {
    
    if (BRIGHTNESS <= 95) BRIGHTNESS += 5;
  
  }  else if (mouseX > 520 && mouseX < 545 && mouseY > SCREEN_SIZE+4 && mouseY < SCREEN_SIZE+19) {
    
    // Bright down checkbox  
    SATURATION -= 10;
    if (SATURATION < 0) SATURATION = 1;
   
    // Bright up checkbox
  } else if (mouseX > 520 && mouseX < 545 && mouseY > SCREEN_SIZE+22 && mouseY < SCREEN_SIZE+37) {
    
    SATURATION += 10;
    if (SATURATION > 255) SATURATION = 255;
  
  }  else if (mouseX > 400 && mouseX < 420 && mouseY > SCREEN_SIZE+10 && mouseY < SCREEN_SIZE+30) {
    // No color correction  
    COLOR_STATE = 0;
   
  }  else if (mouseX > 340 && mouseX < 355 && mouseY > SCREEN_SIZE+4 && mouseY < SCREEN_SIZE+19) {
    // None red  
    COLOR_STATE = 1;
   
  }  else if (mouseX > 340 && mouseX < 355 && mouseY > SCREEN_SIZE+22 && mouseY < SCREEN_SIZE+37) {
    // All red  
    COLOR_STATE = 4;
   
  }  else if (mouseX > 360 && mouseX < 375 && mouseY > SCREEN_SIZE+4 && mouseY < SCREEN_SIZE+19) {
    // None blue  
    COLOR_STATE = 2;
   
  }  else if (mouseX > 360 && mouseX < 375 && mouseY > SCREEN_SIZE+22 && mouseY < SCREEN_SIZE+37) {
    // All blue  
    COLOR_STATE = 5;
   
  }  else if (mouseX > 380 && mouseX < 395 && mouseY > SCREEN_SIZE+4 && mouseY < SCREEN_SIZE+19) {
    // None green  
    COLOR_STATE = 3;
   
  }  else if (mouseX > 380 && mouseX < 395 && mouseY > SCREEN_SIZE+22 && mouseY < SCREEN_SIZE+37) {
    // All green  
    COLOR_STATE = 6;
  
  }
}


// Coord class

class Coord {
  public int x, y;
  
  Coord(int x, int y) {
    this.x = x;
    this.y = y;
  }
}

void setCellColor(color c, byte s, int p) {
  if (p >= LEDS) {
    println("invalid LED number: i only have " + LEDS + " LEDs");
    return;
  }
  if (s >= STRIPS) {
    println("invalid strip number: i only have " + STRIPS + " strips");
    return;
  }
  // pix_color[s][p] = c; // Send color out to screen
}

//
// drawLabels
//
void drawLabels() {
}

//
//  Server Routines
//
void pollServer() {
  try {
    Client c = _server.available();
    // append any available bytes to the buffer
    if (c != null) {
      _buf.append(c.readString());
    }
    // process as many lines as we can find in the buffer
    int ix = _buf.indexOf("\n");
    while (ix > -1) {
      String msg = _buf.substring(0, ix);
      msg = msg.trim();
      //println(msg);
      processCommand(msg);
      _buf.delete(0, ix+1);
      ix = _buf.indexOf("\n");
    }
  } catch (Exception e) {
    println("exception handling network command");
    e.printStackTrace();
  }  
}

Pattern cmd_pattern = Pattern.compile("^\\s*(\\d+),(\\d+),(\\d+),(\\d+),(\\d+)\\s*$");

void processCommand(String cmd) {
  if (cmd.charAt(0) == 'X') {  // Finish the cycle
    finishCycle();
  } else if (cmd.charAt(0) == 'D') {  // Get the delay time
    delay_time = Integer.valueOf(cmd.substring(1, cmd.length())) + 20;  // 20 is a buffer-time
  } else {  
    processPixelCommand(cmd);  // Pixel command
  }
}
  
void processPixelCommand(String cmd) {
  Matcher m = cmd_pattern.matcher(cmd);
  if (!m.find()) {
    println("ignoring input!");
    return;
  }
  byte strip  = Byte.valueOf(m.group(1));
  int pix    = Integer.valueOf(m.group(2));
  int r     = Integer.valueOf(m.group(3));
  int g     = Integer.valueOf(m.group(4));
  int b     = Integer.valueOf(m.group(5));
  
  //println(String.format("setting pixel:(%d,%d) to r:%d g:%d b:%d", strip, pix, h, s, v));
  setPixelBuffer(strip, pix, (char)r, (char)g, (char)b, false); 
}

// Send a corrected color to a eel pixel on screen and in lights
void sendColorOut(byte strip, int pix, char r, char g, char b) {
  color correct = colorCorrect(adj_brightness(r), adj_brightness(g), adj_brightness(b));
  setCellColor(correct, strip, pix);  // Simulator
  setPixelBuffer(strip, pix, r, g, b, true);  // Lights: sets next-frame buffer (doesn't turn them on)
}

//
// Finish Cycle
//
// Get ready for the next morph cycle by:
void finishCycle() {
  morph_frame(1.0);
  pushColorBuffer();
  start_time = millis();  // reset the clock
}

//
// Update Morph
//
void update_morph() {
  if ((last_time - start_time) > delay_time) {
    return;  // Already finished all morphing - waiting for next command 
  }
  last_time = millis();  // update clock
  morph_frame((last_time - start_time) / (float)delay_time); 
}
  
//
//  Fractional morphing between current and next frame - sends data to lights
//
//  fract is an 0.0-1.0 fraction towards the next frame
//
void morph_frame(float fract) {
  byte strip;
  char r,g,b;
  int pix;
  
  for (strip = 0; strip < STRIPS; strip++) {
    for (pix = 0; pix < LEDS; pix++) {
      if (hasChanged(strip, pix)) {
        r = interp(curr_buffer[strip][pix][0], next_buffer[strip][pix][0], fract);
        g = interp(curr_buffer[strip][pix][1], next_buffer[strip][pix][1], fract);
        b = interp(curr_buffer[strip][pix][2], next_buffer[strip][pix][2], fract);
        
        sendColorOut(strip, pix, r, g, b);  // Update individual light and simulator
      }
    }
  }
 
  sendDataToLights();  // Turn on all lights
  if (UPDATE_VISUALIZER) {
    //drawEels();  // Update all displays
    drawLabels();
  }
}  

char interp(char a, char b, float fract) {
  return (char)(a + (fract * (b-a)));
}

//
//  Routines to interact with the Lights
//
void sendDataToLights() {
  byte strip;
  int pixel;
  
  if (testObserver.hasStrips) {   
    registry.startPushing();
    registry.setExtraDelay(0);
    registry.setAutoThrottle(true);
    registry.setAntiLog(true);    
    
    List<Strip> strips = registry.getStrips();
    strip = 0;
    
    for (Strip s : strips) {      
      for (pixel = 0; pixel < LEDS; pixel++) {
         if (hasChanged(strip, pixel)) {
           s.setPixel(getPixelBuffer(strip, pixel), pixel);
         }
      }
      strip++;
      if (strip >= STRIPS) break;  // Prevents buffer overflow
    }
  }
}

private void prepareExitHandler () {

  Runtime.getRuntime().addShutdownHook(new Thread(new Runnable() {

    public void run () {

      System.out.println("Shutdown hook running");

      List<Strip> strips = registry.getStrips();
      for (Strip strip : strips) {
        for (int i=0; i<strip.getLength(); i++)
          strip.setPixel(#000000, i);
      }
      for (int i=0; i<100000; i++)
        Thread.yield();
    }
  }
  ));
}

//
//  Handling global brightness
//
char adj_brightness(float value) {
  return (char)(value * BRIGHTNESS / 100);
}

color colorCorrect(int r, int g, int b) {
  switch(COLOR_STATE) {
    case 1:  // no red
      if (r > 0) {
        if (g == 0) {
          g = r;
          r = 0;
        } else if (b == 0) {
          b = r;
          r = 0;
        }
      }
      break;
    
    case 2:  // no green
      if (g > 0) {
        if (r == 0) {
          r = g;
          g = 0;
        } else if (b == 0) {
          b = g;
          g = 0;
        }
      }
      break;
    
    case 3:  // no blue
      if (b > 0) {
        if (r == 0) {
          r = b;
          b = 0;
        } else if (g == 0) {
          g = b;
          b = 0;
        }
      }
      break;
    
    case 4:  // all red
      if (r == 0) {
        if (g > b) {
          r = g;
          g = 0;
        } else {
          r = b;
          b = 0;
        }
      }
      break;
    
    case 5:  // all green
      if (g == 0) {
        if (r > b) {
          g = r;
          r = 0;
        } else {
          g = b;
          b = 0;
        }
      }
      break;
    
    case 6:  // all blue
      if (b == 0) {
        if (r > g) {
          b = r;
          r = 0;
        } else {
          b = g;
          g = 0;
        }
      }
      break;
    
    default:
      break;
  }
  return color(r,g,b);   
}

void initializeColorBuffers() {
  char empty = 0;
  for (byte s = 0; s < STRIPS; s++) {
    for (int p = 0; p < LEDS; p++) {
      setPixelBuffer(s, p, empty,empty,empty, false);
    }
  }
  pushColorBuffer();
}

void setPixelBuffer(byte strip, int pixel, char r, char g, char b, boolean morph) {
  if (morph) {
    morph_buffer[strip][pixel][0] = r;
    morph_buffer[strip][pixel][1] = g;
    morph_buffer[strip][pixel][2] = b;
  } else {
    next_buffer[strip][pixel][0] = r;
    next_buffer[strip][pixel][1] = g;
    next_buffer[strip][pixel][2] = b;
  }
}

color getPixelBuffer(byte strip, int pixel) {
  
  return color(morph_buffer[strip][pixel][0],
               morph_buffer[strip][pixel][1],
               morph_buffer[strip][pixel][2]);
}

boolean hasChanged(byte s, int p) {
  if (curr_buffer[s][p][0] != next_buffer[s][p][0] ||
      curr_buffer[s][p][1] != next_buffer[s][p][1] ||
      curr_buffer[s][p][2] != next_buffer[s][p][2]) {
        return true;
      } else {
        return false;
      }
}

void pushColorBuffer() {
  for (byte s = 0; s < STRIPS; s++) {
    for (int p = 0; p < LEDS; p++) {
      curr_buffer[s][p][0] = next_buffer[s][p][0];
      curr_buffer[s][p][1] = next_buffer[s][p][1];
      curr_buffer[s][p][2] = next_buffer[s][p][2];
    }
  }
}
