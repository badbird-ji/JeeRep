import pygame 
import random 
import time 
 
# ========== 颜色常量 ==========
# 鲜艳马卡龙色系 
COLORS = [
    (0, 0, 0),
    (255, 105, 180),  # 亮粉色马卡龙 - I 
    (98, 205, 98),    # 翠绿色马卡龙 - S 
    (255, 99, 71),    # 鲜红色马卡龙 - Z 
    (65, 105, 225),   # 宝蓝色马卡龙 - J 
    (255, 165, 0),    # 明橙色马卡龙 - L 
    (147, 112, 219),  # 亮紫色马卡龙 - T 
    (255, 215, 0)     # 金黄色马卡龙 - O 
]
 
# 界面颜色 
BG_COLOR = (255, 255, 255)       # 纯白色背景 
GRID_COLOR = (245, 245, 245)     # 更浅的网格 
BORDER_COLOR = (200, 200, 200)   # 灰色边框 
PREVIEW_BG = (252, 250, 248)     # 更白的预览背景 
TEXT_COLOR = (80, 80, 80)        # 深灰色文字 
SCORE_COLOR = (46, 139, 87)      # 海绿色分数 
LEVEL_UP_COLOR = (255, 140, 0)   # 深橙色升级提示 
GAME_OVER_COLOR = (220, 20, 60)  # 鲜红色游戏结束 
 
# 阴影和发光效果 
SHADOW_SIZE = 1                  # 保持小阴影 
GLOW_COLOR = (255, 255, 255, 15) # 更淡的发光效果 
 
# ========== 方块形状定义 ==========
SHAPES = [
    [[1, 5, 9, 13], [4, 5, 6, 7]],       # I 
    [[4, 5, 9, 10], [2, 6, 5, 9]],       # Z 
    [[6, 7, 9, 10], [1, 5, 6, 10]],      # S 
    [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],  # L 
    [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]], # J 
    [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],   # T 
    [[1, 2, 5, 6]],                      # O 
]
 
# ========== 游戏初始化 ==========
pygame.init() 
pygame.mixer.init()   # 初始化音频系统 
 
# 加载音效 
try:
    MOVE_SOUND = pygame.mixer.Sound("sounds/move.wav") 
    ROTATE_SOUND = pygame.mixer.Sound("sounds/rotate.wav") 
    DROP_SOUND = pygame.mixer.Sound("sounds/drop.wav") 
    CLEAR_SOUND = pygame.mixer.Sound("sounds/clear.wav") 
    LEVEL_UP_SOUND = pygame.mixer.Sound("sounds/level_up.wav") 
    GAME_OVER_SOUND = pygame.mixer.Sound("sounds/game_over.wav") 
 
    # 设置音量 
    MOVE_SOUND.set_volume(0.3) 
    ROTATE_SOUND.set_volume(0.3) 
    DROP_SOUND.set_volume(0.4) 
    CLEAR_SOUND.set_volume(0.5) 
    LEVEL_UP_SOUND.set_volume(0.6) 
    GAME_OVER_SOUND.set_volume(0.7) 
 
    sounds_loaded = True 
except:
    print("警告：无法加载音效文件，游戏将在无声模式下运行")
    sounds_loaded = False 
 
# ========== Tetris 类 ==========
class Tetris:
    def __init__(self, height, width):
        self.height  = height 
        self.width  = width 
        self.field  = []
        self.score  = 0 
        self.level  = 1 
        self.state  = "start"
        self.figure  = None 
        self.next_figure  = None 
        self.show_score_animation  = False 
        self.score_animation_counter  = 0 
        self.last_score  = 0 
        self.score_increase  = 0 
        self.x = (500 - width * ZOOM) // 2 
        self.y = 50 
        self.init_field() 
 
    def init_field(self):
        """初始化游戏场地"""
        self.field  = []
        for i in range(self.height): 
            new_line = []
            for j in range(self.width): 
                new_line.append(0) 
            self.field.append(new_line) 
 
    def new_figure(self):
        """生成新方块"""
        if self.next_figure  is None:
            self.next_figure  = Figure(3, 0)
        
        self.figure  = self.next_figure  
        self.next_figure  = Figure(3, 0)
        
        if self.intersects(): 
            self.state  = "gameover"
            if sounds_loaded:
                GAME_OVER_SOUND.play() 
 
    def intersects(self):
        """检查碰撞"""
        intersection = False 
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image(): 
                    if (i + self.figure.y  > self.height  - 1 or 
                            j + self.figure.x  > self.width  - 1 or 
                            j + self.figure.x  < 0 or 
                            self.field[i  + self.figure.y][j  + self.figure.x]  > 0):
                        intersection = True 
        return intersection 
 
    def freeze(self):
        """固定方块到场地"""
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image(): 
                    self.field[i  + self.figure.y][j  + self.figure.x]  = self.figure.color  
        
        self.break_lines() 
        self.new_figure() 
        
        if self.intersects(): 
            self.state  = "gameover"
 
    def break_lines(self):
        """消除完整的行"""
        lines = 0 
        for i in range(1, self.height): 
            zeros = 0 
            for j in range(self.width): 
                if self.field[i][j]  == 0:
                    zeros += 1 
            
            if zeros == 0:
                lines += 1 
                for i1 in range(i, 1, -1):
                    for j in range(self.width): 
                        self.field[i1][j]  = self.field[i1-1][j] 
 
        if lines > 0:
            if sounds_loaded:
                CLEAR_SOUND.play() 
            
            self.score_increase  = lines ** 2 
            self.last_score  = self.score  
            self.score  += self.score_increase  
            self.show_score_animation  = True 
            self.score_animation_counter  = 30 
 
            # 检查是否升级 
            old_level = self.level  
            self.level  = min(10, self.score  // 1000 + 1)
            if self.level  > old_level:
                if sounds_loaded:
                    LEVEL_UP_SOUND.play() 
                self.show_level_up  = True 
                self.level_up_counter  = 60 
 
    def go_space(self):
        """硬降落"""
        while not self.intersects(): 
            self.figure.y  += 1 
        self.figure.y  -= 1 
        self.freeze() 
        if sounds_loaded:
            DROP_SOUND.play() 
 
    def go_down(self):
        """向下移动"""
        self.figure.y  += 1 
        if self.intersects(): 
            self.figure.y  -= 1 
            self.freeze() 
            if sounds_loaded:
                DROP_SOUND.play() 
 
    def go_side(self, dx):
        """横向移动"""
        old_x = self.figure.x  
        self.figure.x  += dx 
        if self.intersects(): 
            self.figure.x  = old_x 
        elif sounds_loaded:
            MOVE_SOUND.play() 
 
    def rotate(self):
        """旋转方块"""
        old_rotation = self.figure.rotation  
        self.figure.rotate() 
        if self.intersects(): 
            self.figure.rotation  = old_rotation 
        elif sounds_loaded:
            ROTATE_SOUND.play() 
 
    def draw_block(self, screen, x, y, color, with_shadow=True, preview=False):
        """绘制单个方块"""
        zoom = PREVIEW_ZOOM if preview else ZOOM 
        
        if with_shadow:
            # 绘制更深的阴影 
            shadow_color = (220, 220, 220)
            pygame.draw.rect(screen,  shadow_color,
                            [x + SHADOW_SIZE, y + SHADOW_SIZE,
                             zoom - 2, zoom - 2])
 
        # 绘制方块主体 
        pygame.draw.rect(screen,  color,
                        [x, y, zoom - 2, zoom - 2])
 
        # 添加明显的高光效果 
        highlight_color = (min(color[0] + 40, 255),
                          min(color[1] + 40, 255),
                          min(color[2] + 40, 255))
        pygame.draw.line(screen,  highlight_color,
                        (x, y), (x + zoom - 2, y), 2)
        pygame.draw.line(screen,  highlight_color,
                        (x, y), (x, y + zoom - 2), 2)
 
    def draw(self, screen):
        """绘制整个游戏界面"""
        screen.fill(BG_COLOR) 
 
        # 绘制游戏区域的发光效果 
        s = pygame.Surface((self.width  * ZOOM + SHADOW_SIZE * 4,
                          self.height  * ZOOM + SHADOW_SIZE * 4),
                          pygame.SRCALPHA)
        pygame.draw.rect(s,  GLOW_COLOR,
                        [0, 0, s.get_width(),  s.get_height()]) 
        screen.blit(s,  (self.x - SHADOW_SIZE * 2,
                       self.y - SHADOW_SIZE * 2))
 
        # 绘制游戏区域背景 
        pygame.draw.rect(screen,  PREVIEW_BG,
                        [self.x - SHADOW_SIZE,
                         self.y - SHADOW_SIZE,
                         self.width  * ZOOM + SHADOW_SIZE * 2,
                         self.height  * ZOOM + SHADOW_SIZE * 2])
 
        # 绘制渐变边框 
        for i in range(3):
            pygame.draw.rect(screen,  BORDER_COLOR,
                            [self.x - 1 - i,
                             self.y - 1 - i,
                             self.width  * ZOOM + 2 + i * 2,
                             self.height  * ZOOM + 2 + i * 2], 1)
 
        # 绘制网格和已放置的方块 
        for i in range(self.height): 
            for j in range(self.width): 
                pygame.draw.rect(screen,  GRID_COLOR,
                                [self.x + j * ZOOM,
                                 self.y + i * ZOOM,
                                 ZOOM, ZOOM], 1)
                if self.field[i][j]  > 0:
                    self.draw_block(screen, 
                                   self.x + j * ZOOM,
                                   self.y + i * ZOOM,
                                   COLORS[self.field[i][j]])
 
        # 绘制当前下落的方块 
        if self.figure  is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j 
                    if p in self.figure.image(): 
                        self.draw_block(screen, 
                                       self.x + (j + self.figure.x)  * ZOOM,
                                       self.y + (i + self.figure.y)  * ZOOM,
                                       COLORS[self.figure.color])
 
        # 绘制分数和等级显示区域 
        self.draw_stats(screen) 
 
        # 绘制预览区域 
        self.draw_preview(screen) 
 
        # 绘制游戏结束画面 
        if self.state  == "gameover":
            self.draw_game_over(screen) 
 
        pygame.display.flip() 
 
    def draw_stats(self, screen):
        """绘制分数和等级信息"""
        text_score = game_font.render(f" 得分: {self.score}",  True, TEXT_COLOR)
        text_level = game_font.render(f" 等级: {self.level}",  True, TEXT_COLOR)
        screen.blit(text_score,  [25, 20])
        screen.blit(text_level,  [25, 50])
 
        # 显示分数增加动画 
        if self.show_score_animation  and self.score_animation_counter  > 0:
            animation_y = 60 - (30 - self.score_animation_counter) 
            alpha = min(255, self.score_animation_counter  * 8)
            score_text = score_font.render(f"+{self.score_increase}", 
                                         True, SCORE_COLOR)
            screen.blit(score_text,  [25, animation_y])
            self.score_animation_counter  -= 1 
            if self.score_animation_counter  <= 0:
                self.show_score_animation  = False 
 
        # 显示升级提示 
        if hasattr(self, 'show_level_up') and self.show_level_up  and self.level_up_counter  > 0:
            level_text = title_font.render(f" 升级到 {self.level}  级！",
                                         True, LEVEL_UP_COLOR)
            text_width = level_text.get_width() 
            screen.blit(level_text,  [(500 - text_width) // 2, 150])
            self.level_up_counter  -= 1 
            if self.level_up_counter  <= 0:
                self.show_level_up  = False 
 
    def draw_preview(self, screen):
        """绘制下一个方块预览区域"""
        preview_width = 4 * PREVIEW_ZOOM 
        preview_height = 4 * PREVIEW_ZOOM 
        preview_x = self.x + self.width  * ZOOM + 20 
        preview_y = self.y + 60 
 
        # 绘制预览区域标题 
        text_next = preview_font.render(" 下一个", True, TEXT_COLOR)
        text_width = text_next.get_width() 
        screen.blit(text_next, 
                   [preview_x + (preview_width - text_width) // 2,
                    preview_y - 25])
 
        # 绘制预览区域边框 
        pygame.draw.rect(screen,  BORDER_COLOR,
                        [preview_x, preview_y,
                         preview_width, preview_height], 1)
 
        # 绘制预览区域网格 
        for i in range(4):
            for j in range(4):
                pygame.draw.rect(screen,  GRID_COLOR,
                                [preview_x + j * PREVIEW_ZOOM,
                                 preview_y + i * PREVIEW_ZOOM,
                                 PREVIEW_ZOOM, PREVIEW_ZOOM], 1)
 
        # 绘制预览方块 
        if self.next_figure  is not None:
            min_x = min([j for i in range(4) for j in range(4)
                        if i * 4 + j in self.next_figure.image()]) 
            max_x = max([j for i in range(4) for j in range(4)
                        if i * 4 + j in self.next_figure.image()]) 
            min_y = min([i for i in range(4) for j in range(4)
                        if i * 4 + j in self.next_figure.image()]) 
            max_y = max([i for i in range(4) for j in range(4)
                        if i * 4 + j in self.next_figure.image()]) 
 
            block_width = max_x - min_x + 1 
            block_height = max_y - min_y + 1 
            offset_x = (4 - block_width) // 2 
            offset_y = (4 - block_height) // 2 
 
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j 
                    if p in self.next_figure.image(): 
                        self.draw_block(screen, 
                                      preview_x + (j - min_x + offset_x) * PREVIEW_ZOOM,
                                      preview_y + (i - min_y + offset_y) * PREVIEW_ZOOM,
                                      COLORS[self.next_figure.color],
                                      preview=True)
 
    def draw_game_over(self, screen):
        """绘制游戏结束画面"""
        # 创建半透明遮罩 
        s = pygame.Surface((500, 600))
        s.set_alpha(120) 
        s.fill((240,  240, 240))
        screen.blit(s,  (0, 0))
 
        # 绘制游戏结束文字 
        text_game_over = title_font.render(" 游戏结束", True, GAME_OVER_COLOR)
        text_restart = title_font.render(" 按 ESC 重新开始", True, TEXT_COLOR)
 
        game_over_width = text_game_over.get_width() 
        restart_width = text_restart.get_width() 
 
        screen.blit(text_game_over,  [(500 - game_over_width) // 2, 200])
        screen.blit(text_restart,  [(500 - restart_width) // 2, 265])
 
# ========== Figure 类 ==========
class Figure:
    def __init__(self, x, y):
        self.x = x 
        self.y = y 
        self.type  = random.randint(0,  len(SHAPES)-1)
        self.color  = self.type  + 1  # 根据方块类型设置固定颜色 
        self.rotation  = 0 
 
    def image(self):
        """获取当前旋转状态的方块形状"""
        return SHAPES[self.type][self.rotation]
 
    def rotate(self):
        """旋转方块"""
        self.rotation  = (self.rotation  + 1) % len(SHAPES[self.type])
 
# ========== 主游戏循环 ==========
try:
    # 初始化游戏窗口 
    size = (500, 600)
    screen = pygame.display.set_mode(size) 
    pygame.display.set_caption(" 俄罗斯方块")
 
    # 游戏常量 
    GAME_HEIGHT = 20 
    GAME_WIDTH = 10 
    ZOOM = 25        # 游戏区域方块大小 
    PREVIEW_ZOOM = 20 # 预览区域方块大小 
    FPS = 60         # 提高刷新率 
    MOVE_DELAY = 6   # 持续移动时每次移动的延迟帧数 
 
    # 设置字体 
    try:
        game_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf",  20)
        score_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf",  16)
        title_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf",  36)
        preview_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf",  16)
    except:
        try:
            game_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc",  20)
            score_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc",  16)
            title_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc",  36)
            preview_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc",  16)
        except:
            print("警告：无法加载中文字体，将使用系统默认字体")
            game_font = pygame.font.Font(None,  20)
            score_font = pygame.font.Font(None,  16)
            title_font = pygame.font.Font(None,  36)
            preview_font = pygame.font.Font(None,  16)
 
    # 创建游戏对象 
    game = Tetris(GAME_HEIGHT, GAME_WIDTH)
    clock = pygame.time.Clock() 
    fps = 60 
    counter = 0 
    move_counter = 0 
 
    pressing_down = False 
    pressing_left = False 
    pressing_right = False 
    done = False 
 
    # 主游戏循环 
    while not done:
        try:
            if game.figure  is None:
                game.new_figure() 
 
            counter += 1 
            if counter > 100000:
                counter = 0 
 
            # 处理持续按键移动 
            current_time = pygame.time.get_ticks() 
 
            # 左右移动处理 
            if pressing_left or pressing_right:
                move_counter += 1 
                if move_counter > MOVE_DELAY:
                    if pressing_left:
                        game.go_side(-1) 
                    if pressing_right:
                        game.go_side(1) 
                    move_counter = 0 
            else:
                move_counter = MOVE_DELAY  # 重置计数器，确保第一次按下时立即移动 
 
            # 根据等级调整下落速度 
            frames_per_drop = max(6, 54 - (game.level  * 6))
            if counter % frames_per_drop == 0 or pressing_down:
                if game.state  == "start":
                    game.go_down() 
 
            # 事件处理 
            for event in pygame.event.get(): 
                if event.type  == pygame.QUIT:
                    done = True 
                elif event.type  == pygame.KEYDOWN:
                    if event.key  == pygame.K_UP:
                        game.rotate() 
                    elif event.key  == pygame.K_DOWN:
                        pressing_down = True 
                    elif event.key  == pygame.K_LEFT:
                        pressing_left = True 
                        if not pressing_right:  # 防止同时按下左右键 
                            game.go_side(-1) 
                        move_counter = 0  # 重置移动计数器 
                    elif event.key  == pygame.K_RIGHT:
                        pressing_right = True 
                        if not pressing_left:  # 防止同时按下左右键 
                            game.go_side(1) 
                        move_counter = 0  # 重置移动计数器 
                    elif event.key  == pygame.K_SPACE:
                        game.go_space() 
                    elif event.key  == pygame.K_ESCAPE:
                        # ESC键总是重新开始游戏 
                        game.__init__(GAME_HEIGHT, GAME_WIDTH)
                elif event.type  == pygame.KEYUP:
                    if event.key  == pygame.K_DOWN:
                        pressing_down = False 
                    elif event.key  == pygame.K_LEFT:
                        pressing_left = False 
                        move_counter = MOVE_DELAY  # 重置移动延迟 
                    elif event.key  == pygame.K_RIGHT:
                        pressing_right = False 
                        move_counter = MOVE_DELAY  # 重置移动延迟 
 
            # 绘制游戏画面 
            try:
                game.draw(screen) 
                pygame.display.flip() 
            except pygame.error  as e:
                print(f"绘制错误：{e}")
                break 
 
            # 控制游戏速度 
            try:
                clock.tick(fps) 
            except:
                print("警告：帧率控制失败")
 
        except Exception as e:
            print(f"游戏循环错误：{e}")
            break 
 
except Exception as e:
    print(f"游戏初始化错误：{e}")
 
finally:
    # 确保正确退出 
    try:
        pygame.quit() 
    except:
        pass 
 
print("游戏已安全退出")