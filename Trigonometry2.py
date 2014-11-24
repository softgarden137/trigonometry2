from System import * # for Uri
from System.Windows import * 
from System.Windows.Controls import UserControl, Canvas
from System.Windows.Shapes import * # exposes Rectangle to scope since not added by default
from System.Windows.Media.Animation import * # exposes Storyboard
#from System.Windows.Media.Imaging import * # for bitmap
from System.Net import * # for WebClient
from System.Windows.Resources import * # for WebClient
#from System.Xml import *
#from System.Xml.Linq import *
from System.Diagnostics import * # enables outputing to a debug window!
from System.Windows.Markup import * # for XamlReader
from Microsoft.Scripting.Silverlight.DynamicApplication import MakeUri

layoutRoot = me.LayoutRoot
curves = me.curves
nodes = me.nodes
bkg = me.bkg
bkgScale = me.bkgScale

_node = None
_curve = None
sb = None
screenDepth = 1000
origin = Point(300, 200)
convertToRadians = Math.PI / 180
x_axis_rotation = 0
y_axis_rotation = 5
z_axis_rotation = 0
mouse = Point(0, 0)
follow = Point(0, 0)
#tuple
names = ( 'Leto I', 'Paul', 'Jessica', 'Alia', 'Thufir', 'Gurney', 'Duncan', 'Yueh', 'Leto II', 'Siona','Vladimir', 'Feyd', 
    'Rabban', 'Irulan' , 'Gaius', 'Hwi Noree', 'Stilgar', 'Liet-Kynes', 'Shaddam', 'Piter')
isDrag = False

_node_xaml_str = """
<UserControl xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <Canvas x:Name="LayoutRoot">
    <Canvas.RenderTransform>
      <TransformGroup>
        <TranslateTransform x:Name="offset" X="0" Y="0"></TranslateTransform>
        <ScaleTransform x:Name="scale" ScaleX="1" ScaleY="1"></ScaleTransform>
        <RotateTransform x:Name="rotation" Angle="0"></RotateTransform>
      </TransformGroup>
    </Canvas.RenderTransform>
    <Rectangle x:Name="bkg" Width="60" Height="18" StrokeThickness="0.5" RadiusX="2" RadiusY="2" Opacity="1.0">
      <Rectangle.Fill>
        <LinearGradientBrush EndPoint="0.5,1" StartPoint="0.5,0">
          <GradientStop Color="#FF326CA7" Offset="0.031"></GradientStop>
          <GradientStop Color="#CCEDF5FF" Offset="1"></GradientStop>
        </LinearGradientBrush>
      </Rectangle.Fill>
      <Rectangle.Stroke>
        <LinearGradientBrush EndPoint="0.5,1" StartPoint="0.5,0">
          <GradientStop Color="#B2FFFFFF"></GradientStop>
          <GradientStop Color="#00FFFFFF" Offset="1"></GradientStop>
        </LinearGradientBrush>
      </Rectangle.Stroke>
    </Rectangle>
    <TextBlock x:Name="display" Canvas.Left="5" Canvas.Top="3" Text="Silverlight" Foreground="#FFFFFFFF" FontSize="11" FontFamily="Arial" FontWeight="Normal"></TextBlock>
  </Canvas>
</UserControl>
"""

_curve_xaml_str = """
<UserControl xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <Canvas x:Name="LayoutRoot">
    <Path Canvas.Left="0" Width="100" Height="100" Data="M-0.3545306,-0.46517369                C-0.3545306,-0.46517369 14.084648,30.19025 29.166666,30.5" Stretch="Fill" Stroke="#FFFFFFFF" StrokeThickness="1" StrokeDashArray="1 3" Canvas.Top="0">
      <Path.RenderTransform>
        <ScaleTransform x:Name="scale" ScaleX="1" ScaleY="1"></ScaleTransform>
      </Path.RenderTransform>
    </Path>
  </Canvas>
</UserControl>
"""

class Node(UserControl):
    def __init__(self, xaml):
        self.xaml = xaml
        
        self.perspective_ratio = 1
        self.X_3d = 0
        self.Y_3d = 0
        self.Z_3d = 0
        self.c = None
    
        def CreateObject(value):
            return XamlReader.Load(value)
            
        self.Content = CreateObject(self.xaml)
        
    def SetX(self, value):
        self.SetValue(Canvas.LeftProperty, Convert.ToDouble(value))
    def GetX(self):
        return self.GetValue(Canvas.LeftProperty)
    X = property(GetX, SetX)
    
    def SetY(self, value):
        self.SetValue(Canvas.TopProperty, Convert.ToDouble(value))
    def GetY(self):
        return self.GetValue(Canvas.TopProperty)
    Y = property(GetY, SetY)
            
class Curve(UserControl):
    def __init__(self, xaml):
        self.xaml = xaml
    
        def CreateObject(value):
            return XamlReader.Load(value)
            
        self.Content = CreateObject(self.xaml)
        
    def SetX(self, value):
        self.SetValue(Canvas.LeftProperty, Convert.ToDouble(value))
    def GetX(self):
        return self.GetValue(Canvas.LeftProperty)
    X = property(GetX, SetX)
    
    def SetY(self, value):
        self.SetValue(Canvas.TopProperty, Convert.ToDouble(value))
    def GetY(self):
        return self.GetValue(Canvas.TopProperty)
    Y = property(GetY, SetY)           


def NodeLoaded(sender, e):
    global _node
    _node = e.Result
    LoadCurve()
    
def CurveLoaded(sender, e):
    global _curve
    _curve = e.Result
    Main()


def NodeLoaded2():
    global _node
    _node = _node_xaml_str
    LoadCurve2()
    
def CurveLoaded2():
    global _curve
    _curve = _curve_xaml_str
    Main()
       
def Page_MouseLeftButtonDown(sender, e):
    global mouse
    global isDrag
    global follow
    global layoutRoot
    layoutRoot.CaptureMouse()
    isDrag = True
    mouse = e.GetPosition(layoutRoot)
    follow = e.GetPosition(layoutRoot)
    
def Page_MouseMove(sender, e):
    global mouse
    global layoutRoot
    mouse = e.GetPosition(layoutRoot)
    
def Page_MouseLeftButtonUp(sender, e):
    global isDrag
    global layoutRoot
    layoutRoot.ReleaseMouseCapture()
    isDrag = False
    
def n_MouseLeave(sender, e):
    sender.bkg.Opacity = .6

def n_MouseEnter(sender, e):
    sender.bkg.Opacity = 1.0
    
def sb_Completed(sender, e):
    global sb
    global follow
    global mouse
    global origin
    global convertToRadians
    global x_axis_rotation
    global y_axis_rotation
    global z_axis_rotation
    global bkg
    global bkgScale
    global nodes
    
    follow.X = follow.X + (mouse.X - follow.X) * .13
    follow.Y = follow.Y + (mouse.Y - follow.Y) * .13
    speedY = (mouse.X - follow.X)*.4
    speedX = (mouse.Y - follow.Y)*.4
    targetAlpha = bkg.Opacity
    targetScale = bkgScale.ScaleX
    
    if isDrag:
        targetAlpha = (mouse.X) / 900
        targetScale = 1 + (mouse.Y) / 1200
        x_axis_rotation = speedX / 5
        y_axis_rotation = speedY / 5
    else:
        x_axis_rotation *= .99
        y_axis_rotation *= .99
    
    bkg.Opacity = bkg.Opacity + (targetAlpha - bkg.Opacity) * .08
    bkgScale.ScaleX = bkgScale.ScaleX + (targetScale - bkgScale.ScaleX) * .08
    bkgScale.ScaleY = bkgScale.ScaleX
    sin_x = Math.Sin(x_axis_rotation * convertToRadians)
    cos_x = Math.Cos(x_axis_rotation * convertToRadians)
    sin_y = Math.Sin(y_axis_rotation * convertToRadians)
    cos_y = Math.Cos(y_axis_rotation * convertToRadians)
    sin_z = Math.Sin(z_axis_rotation * convertToRadians)
    cos_z = Math.Cos(z_axis_rotation * convertToRadians)
    left = 0
    top = 0
    for n in nodes.Children:
        rotatedY = (n.Y_3d * cos_x) - (n.Z_3d * sin_x)
        rotatedDepth = (n.Z_3d * cos_x) + (n.Y_3d * sin_x)
        n.Y_3d = rotatedY
        n.Z_3d = rotatedDepth

        rotatedX = (n.X_3d * cos_y) - (n.Z_3d * sin_y)
        rotatedDepth = (n.Z_3d * cos_y) + (n.X_3d * sin_y)
        n.X_3d = rotatedX
        n.Z_3d = rotatedDepth

        rotatedX = (n.X_3d * cos_z) - (n.Y_3d * sin_z)
        rotatedY = (n.Y_3d * cos_z) + (n.X_3d * sin_z)

        n.X_3d = rotatedX
        n.Y_3d = rotatedY
        n.Z_3d = rotatedDepth

        n.perspective_ratio = screenDepth / (screenDepth + n.Z_3d)
        n.Content.scale.ScaleX = n.perspective_ratio
        n.Content.scale.ScaleY = n.perspective_ratio
        n.Content.Opacity = n.perspective_ratio
        left = (n.X_3d * n.perspective_ratio) + origin.X
        top = (n.Y_3d * n.perspective_ratio) + origin.Y
        n.X = left
        n.Y = top
        
        n.c.Content.scale.ScaleX = (n.X - origin.X)/100
        n.c.Content.scale.ScaleY = (n.Y - origin.Y)/100
        n.c.Content.Opacity = n.Content.Opacity
    sb.Begin() # staring again causes fail
        

def LoadNode():
    client = WebClient()
    client.DownloadStringCompleted += NodeLoaded
    client.DownloadStringAsync(MakeUri("node.xaml"))
    
def LoadCurve():
    client = WebClient()
    client.DownloadStringCompleted += CurveLoaded
    client.DownloadStringAsync(MakeUri("curve.xaml"))

def LoadNode2():
    NodeLoaded2()
    
def LoadCurve2():
    CurveLoaded2()
    
def setupNodes():
    global _node
    global _curve
    global names
    global origin
    global curves
    global nodes
    
    totalNodes = names.Count
    for i in range(0, totalNodes):
        c = Curve(_curve)
        c.X = origin.X
        c.Y = origin.Y
        curves.Children.Add(c)
    for i in range(0, totalNodes):
        n = Node(_node)
        n.c = curves.Children[i]
        myAngle = (360/totalNodes) * i
        n.Content.display.Text = names[i]
        n.X_3d = (Math.Cos((myAngle) * convertToRadians) * 100)
        n.Y_3d = (Math.Sin((myAngle) * convertToRadians) * -100)
        n.Z_3d = i * 8 
        n.Content.offset.X = (n.Content.display.ActualWidth + 10) / -2
        n.Content.offset.Y = (n.Content.display.ActualHeight + 6) / -2
        n.Content.bkg.Width = n.Content.display.ActualWidth + 10
        n.Content.bkg.Height = n.Content.display.ActualHeight + 6
        if (i % 2) == 0:
            n.Z_3d = n.Z_3d * -1
        n.Content.MouseEnter +=  n_MouseEnter
        n.Content.MouseLeave +=  n_MouseLeave
        n.Content.bkg.Opacity = .6
        nodes.Children.Add(n)
    
def Main():
    global sb
    sb = Storyboard()
    layoutRoot.Resources.Add("sb", sb)
    
    layoutRoot.MouseLeftButtonDown += Page_MouseLeftButtonDown
    layoutRoot.MouseMove +=  Page_MouseMove
    layoutRoot.MouseLeftButtonUp +=  Page_MouseLeftButtonUp
    sb.Completed += sb_Completed
    
    setupNodes()
       
    sb.Begin()

#LoadNode()
LoadNode2()
